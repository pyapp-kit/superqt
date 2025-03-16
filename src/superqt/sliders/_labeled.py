from __future__ import annotations

import contextlib
from enum import IntEnum, IntFlag, auto
from functools import partial
from typing import TYPE_CHECKING, Any, overload

from qtpy import QtGui
from qtpy.QtCore import Property, QPoint, QSize, Qt, Signal
from qtpy.QtGui import QFontMetrics, QValidator
from qtpy.QtWidgets import (
    QAbstractSlider,
    QBoxLayout,
    QDoubleSpinBox,
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QStyle,
    QStyleOptionSpinBox,
    QVBoxLayout,
    QWidget,
)

from superqt.utils import signals_blocked

from ._sliders import QDoubleRangeSlider, QDoubleSlider, QRangeSlider

if TYPE_CHECKING:
    from collections.abc import Iterable


class LabelPosition(IntEnum):
    NoLabel = 0
    LabelsAbove = auto()
    LabelsBelow = auto()
    LabelsRight = LabelsAbove
    LabelsLeft = LabelsBelow
    LabelsOnHandle = auto()


class EdgeLabelMode(IntFlag):
    NoLabel = 0
    LabelIsRange = auto()
    LabelIsValue = auto()


class _SliderProxy:
    _slider: QSlider

    def value(self) -> Any:
        return self._slider.value()

    def setValue(self, value: Any) -> None:
        self._slider.setValue(value)

    def sliderPosition(self) -> int:
        return self._slider.sliderPosition()

    def setSliderPosition(self, pos: int) -> None:
        self._slider.setSliderPosition(pos)

    def minimum(self) -> int:
        return self._slider.minimum()

    def setMinimum(self, minimum: int) -> None:
        self._slider.setMinimum(minimum)

    def maximum(self) -> int:
        return self._slider.maximum()

    def setMaximum(self, maximum: int) -> None:
        self._slider.setMaximum(maximum)

    def singleStep(self):
        return self._slider.singleStep()

    def setSingleStep(self, step: int) -> None:
        self._slider.setSingleStep(step)

    def pageStep(self) -> int:
        return self._slider.pageStep()

    def setPageStep(self, step: int) -> None:
        self._slider.setPageStep(step)

    def setRange(self, min: int, max: int) -> None:
        self._slider.setRange(min, max)

    def tickInterval(self) -> int:
        return self._slider.tickInterval()

    def setTickInterval(self, interval: int) -> None:
        self._slider.setTickInterval(interval)

    def tickPosition(self) -> QSlider.TickPosition:
        return self._slider.tickPosition()

    def setTickPosition(self, pos: QSlider.TickPosition) -> None:
        self._slider.setTickPosition(pos)

    def triggerAction(self, action: QAbstractSlider.SliderAction) -> None:
        return self._slider.triggerAction(action)

    def invertedControls(self) -> bool:
        return self._slider.invertedControls()

    def setInvertedControls(self, a0: bool) -> None:
        return self._slider.setInvertedControls(a0)

    def invertedAppearance(self) -> bool:
        return self._slider.invertedAppearance()

    def setInvertedAppearance(self, a0: bool) -> None:
        return self._slider.setInvertedAppearance(a0)

    def isSliderDown(self) -> bool:
        return self._slider.isSliderDown()

    def setSliderDown(self, a0: bool) -> None:
        return self._slider.setSliderDown(a0)

    def hasTracking(self) -> bool:
        return self._slider.hasTracking()

    def setTracking(self, enable: bool) -> None:
        return self._slider.setTracking(enable)

    def orientation(self) -> Qt.Orientation:
        return self._slider.orientation()

    def __getattr__(self, name: Any) -> Any:
        return getattr(self._slider, name)


def _handle_overloaded_slider_sig(
    args: tuple, kwargs: dict
) -> tuple[QWidget | None, Qt.Orientation]:
    """Maintaining signature of QSlider.__init__."""
    parent = None
    orientation = Qt.Orientation.Horizontal
    errmsg = (
        "TypeError: arguments did not match any overloaded call:\n"
        "  QSlider(parent: QWidget = None)\n"
        "  QSlider(Qt.Orientation, parent: QWidget = None)"
    )
    if len(args) > 2:
        raise TypeError(errmsg)
    elif len(args) == 2:
        if kwargs:
            raise TypeError(errmsg)
        orientation, parent = args
    elif args:
        if isinstance(args[0], QWidget):
            if kwargs:
                raise TypeError(errmsg)
            parent = args[0]
        else:
            orientation = args[0]
    parent = kwargs.get("parent", parent)
    return parent, orientation


class QLabeledSlider(_SliderProxy, QAbstractSlider):
    editingFinished = Signal()

    _slider_class = QSlider
    _slider: QSlider

    @overload
    def __init__(self, parent: QWidget | None = ...) -> None: ...

    @overload
    def __init__(
        self, orientation: Qt.Orientation, parent: QWidget | None = ...
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        parent, orientation = _handle_overloaded_slider_sig(args, kwargs)

        super().__init__(parent)
        # accept focus events
        fp = self.style().styleHint(QStyle.StyleHint.SH_Button_FocusPolicy)
        self.setFocusPolicy(Qt.FocusPolicy(fp))

        self._slider = self._slider_class(parent=self)
        self._label = SliderLabel(self._slider, connect=self._setValue, parent=self)
        self._edge_label_mode: EdgeLabelMode = EdgeLabelMode.LabelIsValue

        self._rename_signals()
        self._slider.actionTriggered.connect(self.actionTriggered.emit)
        self._slider.rangeChanged.connect(self._on_slider_range_changed)
        self._slider.sliderMoved.connect(self.sliderMoved.emit)
        self._slider.sliderPressed.connect(self.sliderPressed.emit)
        self._slider.sliderReleased.connect(self.sliderReleased.emit)
        self._slider.valueChanged.connect(self._on_slider_value_changed)
        self._label.editingFinished.connect(self.editingFinished)

        self.setOrientation(orientation)

    # ------------------- public API -------------------

    def setOrientation(self, orientation: Qt.Orientation) -> None:
        """Set orientation, value will be 'horizontal' or 'vertical'."""
        self._slider.setOrientation(orientation)
        marg = (0, 0, 0, 0)
        if orientation == Qt.Orientation.Vertical:
            layout = QVBoxLayout()
            layout.addWidget(self._slider, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(1)
        else:
            if self._edge_label_mode == EdgeLabelMode.NoLabel:
                marg = (0, 0, 5, 0)

            layout = QHBoxLayout()  # type: ignore
            layout.addWidget(self._slider)
            layout.addWidget(self._label)
            self._label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.setSpacing(6)

        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        layout.setContentsMargins(*marg)
        self.setLayout(layout)

    def edgeLabelMode(self) -> EdgeLabelMode:
        """Return current `EdgeLabelMode`."""
        return self._edge_label_mode

    def setEdgeLabelMode(self, opt: EdgeLabelMode) -> None:
        """Set the `EdgeLabelMode`.

        Parameters
        ----------
        opt : EdgeLabelMode
            To show no label, use `EdgeLabelMode.NoLabel`. To show the value
            of the slider, use `EdgeLabelMode.LabelIsValue`. To show
            `value / maximum`, use
            `EdgeLabelMode.LabelIsValue | EdgeLabelMode.LabelIsRange`.
        """
        if opt is EdgeLabelMode.LabelIsRange:
            raise ValueError(
                "mode must be one of 'EdgeLabelMode.NoLabel' or "
                "'EdgeLabelMode.LabelIsValue' or"
                "'EdgeLabelMode.LabelIsValue | EdgeLabelMode.LabelIsRange'."
            )

        self._edge_label_mode = opt
        if not self._edge_label_mode:
            self._label.hide()
            w = 5 if self.orientation() == Qt.Orientation.Horizontal else 0
            self.layout().setContentsMargins(0, 0, w, 0)
        if opt & EdgeLabelMode.LabelIsValue:
            if self.isVisible():
                self._label.show()
            self._label.setMode(opt)
            self._label.setValue(self._slider.value())
            self.layout().setContentsMargins(0, 0, 0, 0)
        self._on_slider_range_changed(self.minimum(), self.maximum())

    # putting this after labelMode methods for the sake of mypy
    EdgeLabelMode = EdgeLabelMode

    # --------------------- private api --------------------

    def _on_slider_range_changed(self, min_: int, max_: int) -> None:
        slash = " / " if self._edge_label_mode & EdgeLabelMode.LabelIsValue else ""
        if self._edge_label_mode & EdgeLabelMode.LabelIsRange:
            self._label.setSuffix(f"{slash}{max_}")
        self.rangeChanged.emit(min_, max_)

    def _on_slider_value_changed(self, v: Any) -> None:
        self._label.setValue(v)
        self.valueChanged.emit(v)

    def _setValue(self, value: float) -> None:
        """Convert the value from float to int before setting the slider value."""
        self._slider.setValue(int(value))

    def _rename_signals(self) -> None: ...


class QLabeledDoubleSlider(QLabeledSlider):
    _slider_class = QDoubleSlider
    _slider: QDoubleSlider
    fvalueChanged = Signal(float)
    fsliderMoved = Signal(float)
    frangeChanged = Signal(float, float)

    @overload
    def __init__(self, parent: QWidget | None = ...) -> None: ...

    @overload
    def __init__(
        self, orientation: Qt.Orientation, parent: QWidget | None = ...
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.setDecimals(2)

    def _setValue(self, value: float) -> None:
        """Convert the value from float to int before setting the slider value."""
        self._slider.setValue(value)

    def _rename_signals(self) -> None:
        self.valueChanged = self.fvalueChanged
        self.sliderMoved = self.fsliderMoved
        self.rangeChanged = self.frangeChanged

    def decimals(self) -> int:
        return self._label.decimals()

    def setDecimals(self, prec: int) -> None:
        self._label.setDecimals(prec)


class QLabeledRangeSlider(_SliderProxy, QAbstractSlider):
    valuesChanged = Signal(tuple)
    editingFinished = Signal()

    _slider_class = QRangeSlider
    _slider: QRangeSlider

    @overload
    def __init__(self, parent: QWidget | None = ...) -> None: ...

    @overload
    def __init__(
        self, orientation: Qt.Orientation, parent: QWidget | None = ...
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        parent, orientation = _handle_overloaded_slider_sig(args, kwargs)
        super().__init__(parent)
        self._rename_signals()

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._handle_labels: list[SliderLabel] = []
        self._handle_label_position: LabelPosition = LabelPosition.LabelsAbove

        # for fine tuning label position
        self.label_shift_x = 0
        self.label_shift_y = 0

        self._slider = self._slider_class()
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._slider.sliderPressed.connect(self.sliderPressed.emit)
        self._slider.sliderReleased.connect(self.sliderReleased.emit)
        self._slider.rangeChanged.connect(self.rangeChanged.emit)
        self.sliderMoved = self._slider.slidersMoved

        self._min_label = SliderLabel(
            self._slider,
            alignment=Qt.AlignmentFlag.AlignLeft,
            connect=self._min_label_edited,
        )
        self._max_label = SliderLabel(
            self._slider,
            alignment=Qt.AlignmentFlag.AlignRight,
            connect=self._max_label_edited,
        )
        self._min_label.editingFinished.connect(self.editingFinished)
        self._max_label.editingFinished.connect(self.editingFinished)
        self.setEdgeLabelMode(EdgeLabelMode.LabelIsRange)

        self._slider.valueChanged.connect(self._on_value_changed)
        self._slider.rangeChanged.connect(self._on_range_changed)

        self._on_value_changed(self._slider.value())
        self._on_range_changed(self._slider.minimum(), self._slider.maximum())
        self.setOrientation(orientation)

    # --------------------- public API -------------------

    def handleLabelPosition(self) -> LabelPosition:
        """Return where/whether labels are shown adjacent to slider handles."""
        return self._handle_label_position

    def setHandleLabelPosition(self, opt: LabelPosition) -> None:
        """Set where/whether labels are shown adjacent to slider handles."""
        self._handle_label_position = opt
        for lbl in self._handle_labels:
            lbl.setVisible(bool(opt))
            trans = opt == LabelPosition.LabelsOnHandle
            # TODO: make double clickable to edit
            lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, trans)
        self.setOrientation(self.orientation())

    def edgeLabelMode(self) -> EdgeLabelMode:
        """Return current `EdgeLabelMode`."""
        return self._edge_label_mode

    def setEdgeLabelMode(self, opt: EdgeLabelMode) -> None:
        """Set `EdgeLabelMode`, controls what is shown at the min/max labels."""
        self._edge_label_mode = opt
        if not self._edge_label_mode:
            self._min_label.hide()
            self._max_label.hide()
        else:
            if self.isVisible():
                self._min_label.show()
                self._max_label.show()
            self._min_label.setMode(opt)
            self._max_label.setMode(opt)
        if opt == EdgeLabelMode.LabelIsValue:
            v0, *_, v1 = self._slider.value()
            self._min_label.setValue(v0)
            self._max_label.setValue(v1)
        elif opt == EdgeLabelMode.LabelIsRange:
            self._min_label.setValue(self._slider.minimum())
            self._max_label.setValue(self._slider.maximum())
        self._reposition_labels()

    def setRange(self, min: int, max: int) -> None:
        self._on_range_changed(min, max)

    def _add_labels(self, layout: QBoxLayout, inverted: bool = False) -> None:
        if inverted:
            first, second = self._max_label, self._min_label
        else:
            first, second = self._min_label, self._max_label
        layout.addWidget(first)
        layout.addWidget(self._slider)
        layout.addWidget(second)

    def setOrientation(self, orientation: Qt.Orientation) -> None:
        """Set orientation, value will be 'horizontal' or 'vertical'."""
        self._slider.setOrientation(orientation)
        inverted = self._slider.invertedAppearance()
        marg = (0, 0, 0, 0)
        if orientation == Qt.Orientation.Vertical:
            layout: QBoxLayout = QVBoxLayout()
            layout.setSpacing(1)
            self._add_labels(layout, inverted=not inverted)
            # TODO: set margins based on label width
            if self._handle_label_position == LabelPosition.LabelsLeft:
                marg = (30, 0, 0, 0)
            elif self._handle_label_position == LabelPosition.LabelsRight:
                marg = (0, 0, 20, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            layout = QHBoxLayout()
            layout.setSpacing(7)
            if self._handle_label_position == LabelPosition.LabelsBelow:
                marg = (0, 0, 0, 25)
            elif self._handle_label_position == LabelPosition.LabelsAbove:
                marg = (0, 25, 0, 0)
            self._add_labels(layout, inverted=inverted)

        # remove old layout
        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        self.setLayout(layout)
        layout.setContentsMargins(*marg)
        super().setOrientation(orientation)
        self._reposition_labels()

    def setInvertedAppearance(self, a0: bool) -> None:
        self._slider.setInvertedAppearance(a0)
        self.setOrientation(self._slider.orientation())

    def resizeEvent(self, a0: Any) -> None:
        super().resizeEvent(a0)
        self._reposition_labels()

    # putting this after methods above for the sake of mypy
    LabelPosition = LabelPosition
    EdgeLabelMode = EdgeLabelMode

    def _getBarColor(self) -> QtGui.QBrush:
        return self._slider._style.brush(self._slider._styleOption)

    def _setBarColor(self, color: str) -> None:
        self._slider._style.brush_active = color

    barColor = Property(QtGui.QBrush, _getBarColor, _setBarColor)
    """The color of the bar between the first and last handle."""

    # ------------- private methods ----------------
    def _rename_signals(self) -> None:
        self.valueChanged = self.valuesChanged

    def _reposition_labels(self) -> None:
        if (
            not self._handle_labels
            or self._handle_label_position == LabelPosition.NoLabel
        ):
            return

        horizontal = self.orientation() == Qt.Orientation.Horizontal
        labels_above = self._handle_label_position == LabelPosition.LabelsAbove
        labels_on_handle = self._handle_label_position == LabelPosition.LabelsOnHandle

        last_edge = None
        labels: Iterable[tuple[int, SliderLabel]] = enumerate(self._handle_labels)
        if self._slider.invertedAppearance():
            labels = reversed(list(labels))
        for i, label in labels:
            rect = self._slider._handleRect(i)
            dx = (-label.width() / 2) + 2
            dy = -label.height() / 2
            if labels_above:  # or on the right
                if horizontal:
                    dy *= 3
                else:
                    dx *= -1
            elif labels_on_handle:
                if horizontal:
                    dy += 0.5
                else:
                    dx += 0.5
            else:
                if horizontal:
                    dy *= -1
                else:
                    dx *= 3
            pos = self._slider.mapToParent(rect.center())
            pos += QPoint(int(dx + self.label_shift_x), int(dy + self.label_shift_y))
            if last_edge is not None:
                # prevent label overlap
                if horizontal:
                    pos.setX(int(max(pos.x(), last_edge.x() + label.width() / 2 + 12)))
                else:
                    pos.setY(int(min(pos.y(), last_edge.y() - label.height() / 2 - 4)))
            label.move(pos)
            last_edge = pos
            label.clearFocus()
            label.raise_()
            label.show()
        self.update()

    def _min_label_edited(self, val: float) -> None:
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self.setMinimum(val)
        else:
            v = list(self._slider.value())
            v[0] = val
            self.setValue(v)
        self._reposition_labels()

    def _max_label_edited(self, val: float) -> None:
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self.setMaximum(val)
        else:
            v = list(self._slider.value())
            v[-1] = val
            self.setValue(v)
        self._reposition_labels()

    def _on_value_changed(self, v: tuple[int, ...]) -> None:
        if self._edge_label_mode == EdgeLabelMode.LabelIsValue:
            self._min_label.setValue(v[0])
            self._max_label.setValue(v[-1])

        if len(v) != len(self._handle_labels):
            for lbl in self._handle_labels:
                lbl.setParent(None)
                lbl.deleteLater()
            self._handle_labels.clear()
            for n, val in enumerate(self._slider.value()):
                _cb = partial(self._slider.setSliderPosition, index=n)
                s = SliderLabel(self._slider, parent=self, connect=_cb)
                s.editingFinished.connect(self.editingFinished)
                s.setValue(val)
                self._handle_labels.append(s)
        else:
            for val, label in zip(v, self._handle_labels):
                label.setValue(val)
        self._reposition_labels()

    def _on_range_changed(self, min: int, max: int) -> None:
        if (min, max) != (self._slider.minimum(), self._slider.maximum()):
            self._slider.setRange(min, max)
        for lbl in self._handle_labels:
            lbl.setRange(min, max)
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self._min_label.setValue(min)
            self._max_label.setValue(max)
        self._reposition_labels()

    # def setValue(self, value) -> None:
    #     super().setValue(value)
    #     self.sliderChange(QSlider.SliderValueChange)


class QLabeledDoubleRangeSlider(QLabeledRangeSlider):
    _slider_class = QDoubleRangeSlider
    _slider: QDoubleRangeSlider
    frangeChanged = Signal(float, float)

    @overload
    def __init__(self, parent: QWidget | None = ...) -> None: ...

    @overload
    def __init__(
        self, orientation: Qt.Orientation, parent: QWidget | None = ...
    ) -> None: ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.setDecimals(2)

    def _rename_signals(self) -> None:
        super()._rename_signals()
        self.rangeChanged = self.frangeChanged

    def decimals(self) -> int:
        return self._min_label.decimals()

    def setDecimals(self, prec: int) -> None:
        self._min_label.setDecimals(prec)
        self._max_label.setDecimals(prec)
        for lbl in self._handle_labels:
            lbl.setDecimals(prec)

    def _getBarColor(self) -> QtGui.QBrush:
        return self._slider._style.brush(self._slider._styleOption)

    def _setBarColor(self, color: str) -> None:
        self._slider._style.brush_active = color

    barColor = Property(QtGui.QBrush, _getBarColor, _setBarColor)
    """The color of the bar between the first and last handle."""


class SliderLabel(QDoubleSpinBox):
    def __init__(
        self,
        slider: QSlider,
        parent=None,
        alignment=Qt.AlignmentFlag.AlignCenter,
        connect=None,
    ) -> None:
        super().__init__(parent=parent)
        self._slider = slider
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMode(EdgeLabelMode.LabelIsValue)
        self.setDecimals(0)

        self.setRange(slider.minimum(), slider.maximum())
        slider.rangeChanged.connect(self._update_size)
        self.setAlignment(alignment)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setStyleSheet("background:transparent; border: 0;")
        if connect is not None:
            self.editingFinished.connect(lambda: connect(self.value()))
        self.editingFinished.connect(self._silent_clear_focus)
        self._update_size()

    def setDecimals(self, prec: int) -> None:
        super().setDecimals(prec)
        self._update_size()

    def setValue(self, val: Any) -> None:
        super().setValue(val)
        if self._mode == EdgeLabelMode.LabelIsRange:
            self._update_size()

    def setMaximum(self, max: float) -> None:
        super().setMaximum(max)
        if self._mode == EdgeLabelMode.LabelIsValue:
            self._update_size()

    def setMinimum(self, min: float) -> None:
        super().setMinimum(min)
        if self._mode == EdgeLabelMode.LabelIsValue:
            self._update_size()

    def setMode(self, opt: EdgeLabelMode) -> None:
        # when the edge labels are controlling slider range,
        # we want them to have a big range, but not have a huge label
        self._mode = opt
        if opt == EdgeLabelMode.LabelIsRange:
            self.setMinimum(-9999999)
            self.setMaximum(9999999)
            with contextlib.suppress(Exception):
                self._slider.rangeChanged.disconnect(self.setRange)
        else:
            self.setMinimum(self._slider.minimum())
            self.setMaximum(self._slider.maximum())
            self._slider.rangeChanged.connect(self.setRange)
        self._update_size()

    # --------------- private ----------------

    def _silent_clear_focus(self) -> None:
        with signals_blocked(self):
            self.clearFocus()

    def _update_size(self, *_: Any) -> None:
        # fontmetrics to measure the width of text
        fm = QFontMetrics(self.font())
        h = self.sizeHint().height()
        fixed_content = self.prefix() + self.suffix() + " "

        if self._mode & EdgeLabelMode.LabelIsValue:
            # determine width based on min/max/specialValue
            mintext = self.textFromValue(self.minimum())[:18]
            maxtext = self.textFromValue(self.maximum())[:18]
            w = max(0, _fm_width(fm, mintext + fixed_content))
            w = max(w, _fm_width(fm, maxtext + fixed_content))
            if self.specialValueText():
                w = max(w, _fm_width(fm, self.specialValueText()))
            if self._mode & EdgeLabelMode.LabelIsRange:
                w += 8  # it seems as thought suffix() is not enough
        else:
            w = max(0, _fm_width(fm, self.textFromValue(self.value()))) + 3

        w += 3  # cursor blinking space
        # get the final size hint
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        size = self.style().sizeFromContents(
            QStyle.ContentsType.CT_SpinBox, opt, QSize(w, h), self
        )
        self.setFixedSize(size)

    def validate(
        self, input_: str | None, pos: int
    ) -> tuple[QValidator.State, str, int]:
        # fake like an integer spinbox
        if input_ and "." in input_ and self.decimals() < 1:
            return QValidator.State.Invalid, input_, len(input_)
        return super().validate(input_, pos)


def _fm_width(fm: QFontMetrics, text: str) -> int:
    if hasattr(fm, "horizontalAdvance"):
        return fm.horizontalAdvance(text)
    return fm.width(text)
