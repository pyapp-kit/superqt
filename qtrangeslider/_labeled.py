from enum import IntEnum
from functools import partial

from ._sliders import QDoubleRangeSlider, QDoubleSlider, QRangeSlider
from .qtcompat.QtCore import QPoint, QSize, Qt, Signal
from .qtcompat.QtGui import QFontMetrics, QValidator
from .qtcompat.QtWidgets import (
    QAbstractSlider,
    QApplication,
    QDoubleSpinBox,
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QStyle,
    QStyleOptionSpinBox,
    QVBoxLayout,
    QWidget,
)


class LabelPosition(IntEnum):
    NoLabel = 0
    LabelsAbove = 1
    LabelsBelow = 2
    LabelsRight = 1
    LabelsLeft = 2


class EdgeLabelMode(IntEnum):
    NoLabel = 0
    LabelIsRange = 1
    LabelIsValue = 2


class SliderProxy:
    _slider: QSlider

    def value(self):
        return self._slider.value()

    def setValue(self, value) -> None:
        self._slider.setValue(value)

    def sliderPosition(self):
        return self._slider.sliderPosition()

    def setSliderPosition(self, pos) -> None:
        self._slider.setSliderPosition(pos)

    def minimum(self):
        return self._slider.minimum()

    def setMinimum(self, minimum):
        self._slider.setMinimum(minimum)

    def maximum(self):
        return self._slider.maximum()

    def setMaximum(self, maximum):
        self._slider.setMaximum(maximum)

    def singleStep(self):
        return self._slider.singleStep()

    def setSingleStep(self, step):
        self._slider.setSingleStep(step)

    def pageStep(self):
        return self._slider.pageStep()

    def setPageStep(self, step) -> None:
        self._slider.setPageStep(step)

    def setRange(self, min, max) -> None:
        self._slider.setRange(min, max)

    def tickInterval(self):
        return self._slider.tickInterval()

    def setTickInterval(self, interval) -> None:
        self._slider.setTickInterval(interval)

    def tickPosition(self):
        return self._slider.tickPosition()

    def setTickPosition(self, pos) -> None:
        self._slider.setTickPosition(pos)


def _handle_overloaded_slider_sig(args, kwargs):
    parent = None
    orientation = Qt.Vertical
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


class QLabeledSlider(SliderProxy, QAbstractSlider):
    _slider_class = QSlider
    _slider: QSlider

    def __init__(self, *args, **kwargs) -> None:
        parent, orientation = _handle_overloaded_slider_sig(args, kwargs)

        super().__init__(parent)

        self._slider = self._slider_class()
        self._label = SliderLabel(self._slider, connect=self._slider.setValue)

        self._slider.rangeChanged.connect(self.rangeChanged.emit)
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._slider.valueChanged.connect(self._label.setValue)

        self.setOrientation(orientation)

    def setOrientation(self, orientation):
        """Set orientation, value will be 'horizontal' or 'vertical'."""
        self._slider.setOrientation(orientation)
        if orientation == Qt.Vertical:
            layout = QVBoxLayout()
            layout.addWidget(self._slider, alignment=Qt.AlignHCenter)
            layout.addWidget(self._label, alignment=Qt.AlignHCenter)
            self._label.setAlignment(Qt.AlignCenter)
            layout.setSpacing(1)
        else:
            layout = QHBoxLayout()
            layout.addWidget(self._slider)
            layout.addWidget(self._label)
            self._label.setAlignment(Qt.AlignRight)
            layout.setSpacing(6)

        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class QLabeledDoubleSlider(QLabeledSlider):
    _slider_class = QDoubleSlider
    _slider: QDoubleSlider
    valueChanged = Signal(float)
    rangeChanged = Signal(float, float)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setDecimals(2)

    def decimals(self) -> int:
        return self._label.decimals()

    def setDecimals(self, prec: int):
        self._label.setDecimals(prec)


class QLabeledRangeSlider(SliderProxy, QAbstractSlider):
    valueChanged = Signal(tuple)
    LabelPosition = LabelPosition
    EdgeLabelMode = EdgeLabelMode
    _slider_class = QRangeSlider
    _slider: QRangeSlider

    def __init__(self, *args, **kwargs) -> None:
        parent, orientation = _handle_overloaded_slider_sig(args, kwargs)
        super().__init__(parent)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._handle_labels = []
        self._handle_label_position: LabelPosition = LabelPosition.LabelsAbove

        # for fine tuning label position
        self.label_shift_x = 0
        self.label_shift_y = 0

        self._slider = self._slider_class()
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._slider.rangeChanged.connect(self.rangeChanged.emit)

        self._min_label = SliderLabel(
            self._slider, alignment=Qt.AlignLeft, connect=self._min_label_edited
        )
        self._max_label = SliderLabel(
            self._slider, alignment=Qt.AlignRight, connect=self._max_label_edited
        )
        self.setEdgeLabelMode(EdgeLabelMode.LabelIsRange)

        self._slider.valueChanged.connect(self._on_value_changed)
        self._slider.rangeChanged.connect(self._on_range_changed)

        self._on_value_changed(self._slider.value())
        self._on_range_changed(self._slider.minimum(), self._slider.maximum())
        self.setOrientation(orientation)

    def handleLabelPosition(self) -> LabelPosition:
        return self._handle_label_position

    def setHandleLabelPosition(self, opt: LabelPosition) -> LabelPosition:
        self._handle_label_position = opt
        for lbl in self._handle_labels:
            if not opt:
                lbl.hide()
            else:
                lbl.show()
        self.setOrientation(self.orientation())

    def edgeLabelMode(self) -> EdgeLabelMode:
        return self._edge_label_mode

    def setEdgeLabelMode(self, opt: EdgeLabelMode):
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
        QApplication.processEvents()
        self._reposition_labels()

    def _reposition_labels(self):
        if not self._handle_labels:
            return

        horizontal = self.orientation() == Qt.Horizontal
        labels_above = self._handle_label_position == LabelPosition.LabelsAbove

        last_edge = None
        for i, label in enumerate(self._handle_labels):
            rect = self._slider._handleRect(i)
            dx = -label.width() / 2
            dy = -label.height() / 2
            if labels_above:
                if horizontal:
                    dy *= 3
                else:
                    dx *= -1
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
        self.update()

    def _min_label_edited(self, val):
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self.setMinimum(val)
        else:
            v = list(self._slider.value())
            v[0] = val
            self.setValue(v)
        self._reposition_labels()

    def _max_label_edited(self, val):
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self.setMaximum(val)
        else:
            v = list(self._slider.value())
            v[-1] = val
            self.setValue(v)
        self._reposition_labels()

    def _on_value_changed(self, v):
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
                s.setValue(val)
                self._handle_labels.append(s)
        else:
            for val, label in zip(v, self._handle_labels):
                label.setValue(val)
        self._reposition_labels()

    def _on_range_changed(self, min, max):
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

    def setRange(self, min, max) -> None:
        self._on_range_changed(min, max)

    def setOrientation(self, orientation):
        """Set orientation, value will be 'horizontal' or 'vertical'."""

        self._slider.setOrientation(orientation)
        if orientation == Qt.Vertical:
            layout = QVBoxLayout()
            layout.setSpacing(1)
            layout.addWidget(self._max_label)
            layout.addWidget(self._slider)
            layout.addWidget(self._min_label)
            # TODO: set margins based on label width
            if self._handle_label_position == LabelPosition.LabelsLeft:
                marg = (30, 0, 0, 0)
            elif self._handle_label_position == LabelPosition.NoLabel:
                marg = (0, 0, 0, 0)
            else:
                marg = (0, 0, 20, 0)
            layout.setAlignment(Qt.AlignCenter)
        else:
            layout = QHBoxLayout()
            layout.setSpacing(7)
            if self._handle_label_position == LabelPosition.LabelsBelow:
                marg = (0, 0, 0, 25)
            elif self._handle_label_position == LabelPosition.NoLabel:
                marg = (0, 0, 0, 0)
            else:
                marg = (0, 25, 0, 0)
            layout.addWidget(self._min_label)
            layout.addWidget(self._slider)
            layout.addWidget(self._max_label)

        # remove old layout
        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        self.setLayout(layout)
        layout.setContentsMargins(*marg)
        super().setOrientation(orientation)
        QApplication.processEvents()
        self._reposition_labels()

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self._reposition_labels()


class QLabeledDoubleRangeSlider(QLabeledRangeSlider):
    _slider_class = QDoubleRangeSlider
    _slider: QDoubleRangeSlider
    rangeChanged = Signal(float, float)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setDecimals(2)

    def decimals(self) -> int:
        return self._min_label.decimals()

    def setDecimals(self, prec: int):
        self._min_label.setDecimals(prec)
        self._max_label.setDecimals(prec)
        for lbl in self._handle_labels:
            lbl.setDecimals(prec)


class SliderLabel(QDoubleSpinBox):
    def __init__(
        self, slider: QSlider, parent=None, alignment=Qt.AlignCenter, connect=None
    ) -> None:
        super().__init__(parent=parent)
        self._slider = slider
        self.setFocusPolicy(Qt.ClickFocus)
        self.setMode(EdgeLabelMode.LabelIsValue)
        self.setDecimals(0)

        self.setRange(slider.minimum(), slider.maximum())
        slider.rangeChanged.connect(self._update_size)
        self.setAlignment(alignment)
        self.setButtonSymbols(QSpinBox.NoButtons)
        self.setStyleSheet("background:transparent; border: 0;")
        if connect is not None:
            self.editingFinished.connect(lambda: connect(self.value()))
        self.editingFinished.connect(self.clearFocus)
        self._update_size()

    def setDecimals(self, prec: int) -> None:
        super().setDecimals(prec)
        self._update_size()

    def _update_size(self, *_):
        # fontmetrics to measure the width of text
        fm = QFontMetrics(self.font())
        h = self.sizeHint().height()
        fixed_content = self.prefix() + self.suffix() + " "

        if self._mode == EdgeLabelMode.LabelIsValue:
            # determine width based on min/max/specialValue
            mintext = self.textFromValue(self.minimum())[:18] + fixed_content
            maxtext = self.textFromValue(self.maximum())[:18] + fixed_content
            w = max(0, _fm_width(fm, mintext))
            w = max(w, _fm_width(fm, maxtext))
            if self.specialValueText():
                w = max(w, _fm_width(fm, self.specialValueText()))
        else:
            w = max(0, _fm_width(fm, self.textFromValue(self.value()))) + 3

        w += 3  # cursor blinking space
        # get the final size hint
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        size = self.style().sizeFromContents(QStyle.CT_SpinBox, opt, QSize(w, h), self)
        self.setFixedSize(size)

    def setValue(self, val):
        super().setValue(val)
        if self._mode == EdgeLabelMode.LabelIsRange:
            self._update_size()

    def setMaximum(self, max: int) -> None:
        super().setMaximum(max)
        if self._mode == EdgeLabelMode.LabelIsValue:
            self._update_size()

    def setMinimum(self, min: int) -> None:
        super().setMinimum(min)
        if self._mode == EdgeLabelMode.LabelIsValue:
            self._update_size()

    def setMode(self, opt: EdgeLabelMode):
        # when the edge labels are controlling slider range,
        # we want them to have a big range, but not have a huge label
        self._mode = opt
        if opt == EdgeLabelMode.LabelIsRange:
            self.setMinimum(-9999999)
            self.setMaximum(9999999)
            try:
                self._slider.rangeChanged.disconnect(self.setRange)
            except Exception:
                pass
        else:
            self.setMinimum(self._slider.minimum())
            self.setMaximum(self._slider.maximum())
            self._slider.rangeChanged.connect(self.setRange)
        self._update_size()

    def validate(self, input: str, pos: int):
        # fake like an integer spinbox
        if "." in input and self.decimals() < 1:
            return QValidator.Invalid, input, len(input)
        return super().validate(input, pos)


def _fm_width(fm, text):
    if hasattr(fm, "horizontalAdvance"):
        return fm.horizontalAdvance(text)
    return fm.width(text)
