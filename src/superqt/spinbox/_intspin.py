from enum import Enum

from qtpy.QtCore import QSize, Qt, Signal
from qtpy.QtGui import QFontMetrics, QValidator
from qtpy.QtWidgets import QAbstractSpinBox, QStyle, QStyleOptionSpinBox


class _EmitPolicy(Enum):
    EmitIfChanged = 0
    AlwaysEmit = 1
    NeverEmit = 2


class _AnyIntValidator(QValidator):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def validate(self, input: str, pos: int):
        if not input.lstrip("-"):
            return QValidator.State.Intermediate, input, len(input)
        if input.lstrip("-").isnumeric():
            return QValidator.State.Acceptable, input, len(input)
        return QValidator.State.Invalid, input, len(input)


class QLargeIntSpinBox(QAbstractSpinBox):
    """An integer spinboxes backed by unbound python integer

    Qt's built-in ``QSpinBox`` is backed by a signed 32-bit integer.
    This could become limiting, particularly in large dense segmentations.
    This class behaves like a ``QSpinBox`` backed by an unbound python int.

    Does not yet support "prefix", "suffix" or "specialValue" like QSpinBox.
    """

    textChanged = Signal(str)
    valueChanged = Signal(object)  # object instead of int for large ints

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._value: int = 0
        self._minimum: int = 0
        self._maximum: int = 2**64 - 1
        self._single_step: int = 1
        self._pending_emit = False
        validator = _AnyIntValidator(self)
        self.lineEdit().setValidator(validator)
        self.lineEdit().textChanged.connect(self._editor_text_changed)
        self.setValue(0)

    # ###############  Public Functions  #######################

    def value(self):
        return self._value

    def setValue(self, value):
        self._setValue(value, _EmitPolicy.EmitIfChanged)

    def minimum(self):
        return self._minimum

    def setMinimum(self, min):
        self._minimum = int(min)

    def maximum(self):
        return self._maximum

    def setMaximum(self, max):
        self._maximum = int(max)

    def setRange(self, minimum, maximum):
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def singleStep(self):
        return self._single_step

    def setSingleStep(self, step):
        self._single_step = int(step)

    # TODO: add prefix/suffix/stepType

    # ###############  QtOverrides  #######################

    def focusOutEvent(self, e) -> None:
        if self._pending_emit:
            self._interpret(_EmitPolicy.EmitIfChanged)
        return super().focusOutEvent(e)

    def closeEvent(self, e) -> None:
        if self._pending_emit:
            self._interpret(_EmitPolicy.EmitIfChanged)
        return super().closeEvent(e)

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self._interpret(
                _EmitPolicy.AlwaysEmit
                if self.keyboardTracking()
                else _EmitPolicy.EmitIfChanged
            )
        return super().keyPressEvent(e)

    def stepBy(self, steps: int) -> None:
        step = self._single_step
        old = self._value
        e = _EmitPolicy.EmitIfChanged
        if self._pending_emit:
            self._interpret(_EmitPolicy.NeverEmit)
            if self._value != old:
                e = _EmitPolicy.AlwaysEmit
        self._setValue(self._bound(self._value + (step * steps)), e)

    def stepEnabled(self):
        flags = QAbstractSpinBox.StepEnabledFlag.StepNone
        if self.isReadOnly():
            return flags
        if self._value < self._maximum:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepUpEnabled
        if self._value > self._minimum:
            flags |= QAbstractSpinBox.StepEnabledFlag.StepDownEnabled
        return flags

    def sizeHint(self):
        self.ensurePolished()
        fm = QFontMetrics(self.font())
        h = self.lineEdit().sizeHint().height()
        if hasattr(fm, "horizontalAdvance"):
            # Qt >= 5.11
            w = fm.horizontalAdvance(str(self._value)) + 3
        else:
            w = fm.width(str(self._value)) + 3
        w = max(36, w)
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        hint = QSize(w, h)
        return self.style().sizeFromContents(
            QStyle.ContentsType.CT_SpinBox, opt, hint, self
        )

    # ###############  Implementation Details  #######################

    def _setValue(self, value, policy):
        self._value, old = self._bound(int(value)), self._value
        self._pending_emit = False
        self._updateEdit()
        self.update()

        if policy is _EmitPolicy.AlwaysEmit or (
            policy is _EmitPolicy.EmitIfChanged and self._value != old
        ):
            self._pending_emit = False
            self.textChanged.emit(self.lineEdit().displayText())
            self.valueChanged.emit(self._value)

    def _updateEdit(self):
        new_text = str(self._value)
        if self.lineEdit().text() == new_text:
            return
        self.lineEdit().setText(new_text)

    def _interpret(self, policy):
        text = self.lineEdit().displayText() or str(self._value)
        v = int(text)
        self._setValue(v, policy)

    def _editor_text_changed(self, t):
        if self.keyboardTracking():
            self._setValue(int(t), _EmitPolicy.EmitIfChanged)
            self.lineEdit().setFocus()
            self._pending_emit = False
        else:
            self._pending_emit = True

    def _bound(self, value):
        return max(self._minimum, min(self._maximum, value))
