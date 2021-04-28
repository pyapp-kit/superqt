from enum import IntEnum
from functools import partial

from ._qrangeslider import QRangeSlider
from .qtcompat.QtCore import QPoint, QSize, Qt, Signal
from .qtcompat.QtGui import QFontMetrics
from .qtcompat.QtWidgets import (
    QAbstractSlider,
    QApplication,
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


class QLabeledSlider(QAbstractSlider):
    def __init__(self, *args) -> None:
        parent = None
        orientation = Qt.Horizontal
        if len(args) == 2:
            orientation, parent = args
        elif args:
            if isinstance(args[0], QWidget):
                parent = args[0]
            else:
                orientation = args[0]

        super().__init__(parent)

        self._slider = QSlider()
        self._slider.valueChanged.connect(self.valueChanged.emit)
        self._label = SliderLabel(self._slider, connect=self.setValue)

        self.valueChanged.connect(self._label.setValue)
        self.valueChanged.connect(self._slider.setValue)
        self.rangeChanged.connect(self._slider.setRange)

        self._slider.valueChanged.connect(self.setValue)
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
            layout.setSpacing(10)

        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class QLabeledRangeSlider(QAbstractSlider):
    valueChanged = Signal(tuple)
    LabelPosition = LabelPosition
    EdgeLabelMode = EdgeLabelMode

    def __init__(self, *args) -> None:
        parent = None
        orientation = Qt.Horizontal
        if len(args) == 2:
            orientation, parent = args
        elif args:
            if isinstance(args[0], QWidget):
                parent = args[0]
            else:
                orientation = args[0]

        super().__init__(parent)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._handle_labels = []
        self._handle_label_position: LabelPosition = LabelPosition.LabelsAbove

        # for fine tuning label position
        self.label_shift_x = 0
        self.label_shift_y = 0

        self._slider = QRangeSlider()
        self._slider.valueChanged.connect(self.valueChanged.emit)

        self._min_label = SliderLabel(
            self._slider, alignment=Qt.AlignLeft, connect=self._min_label_edited
        )
        self._max_label = SliderLabel(
            self._slider, alignment=Qt.AlignRight, connect=self._max_label_edited
        )
        self.setEdgeLabelMode(EdgeLabelMode.LabelIsRange)

        self._slider.valueChanged.connect(self._on_value_changed)
        self.rangeChanged.connect(self._on_range_changed)

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

        for label, rect in zip(self._handle_labels, self._slider._handleRects()):
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
            pos += QPoint(dx + self.label_shift_x, dy + self.label_shift_y)
            label.move(pos)
            label.clearFocus()

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
                _cb = partial(self._slider._setSliderPositionAt, n)
                s = SliderLabel(self._slider, parent=self, connect=_cb)
                s.setValue(val)
                self._handle_labels.append(s)
        else:
            for val, label in zip(v, self._handle_labels):
                label.setValue(val)
        self._reposition_labels()

    def _on_range_changed(self, min, max):
        self._slider.setRange(min, max)
        for lbl in self._handle_labels:
            lbl.setRange(min, max)
        if self._edge_label_mode == EdgeLabelMode.LabelIsRange:
            self._min_label.setValue(min)
            self._max_label.setValue(max)
        self._reposition_labels()

    def value(self):
        return self._slider.value()

    def setValue(self, v: int) -> None:
        self._slider.setValue(v)
        self.sliderChange(QSlider.SliderValueChange)

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


class SliderLabel(QSpinBox):
    def __init__(
        self, slider: QSlider, parent=None, alignment=Qt.AlignCenter, connect=None
    ) -> None:
        super().__init__(parent=parent)
        self._slider = slider
        self.setFocusPolicy(Qt.ClickFocus)
        self.setMode(EdgeLabelMode.LabelIsValue)

        self.setRange(slider.minimum(), slider.maximum())
        slider.rangeChanged.connect(self._update_size)
        self.setAlignment(alignment)
        self.setButtonSymbols(QSpinBox.NoButtons)
        self.setStyleSheet("background:transparent; border: 0;")
        if connect is not None:
            self.editingFinished.connect(lambda: connect(self.value()))
        self.editingFinished.connect(self.clearFocus)
        self._update_size()

    def _update_size(self):
        # fontmetrics to measure the width of text
        fm = QFontMetrics(self.font())
        h = self.sizeHint().height()
        fixed_content = self.prefix() + self.suffix() + " "

        if self._mode == EdgeLabelMode.LabelIsValue:
            # determine width based on min/max/specialValue
            s = self.textFromValue(self.minimum())[:18] + fixed_content
            w = max(0, fm.horizontalAdvance(s))
            s = self.textFromValue(self.maximum())[:18] + fixed_content
            w = max(w, fm.horizontalAdvance(s))
            if self.specialValueText():
                w = max(w, fm.horizontalAdvance(self.specialValueText()))
        else:
            s = self.textFromValue(self.value())
            w = max(0, fm.horizontalAdvance(s)) + 3

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
