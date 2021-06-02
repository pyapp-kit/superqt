"""Generic Sliders with internal python-based models

This module reimplements most of the logic from qslider.cpp in python:
https://code.woboq.org/qt5/qtbase/src/widgets/widgets/qslider.cpp.html

This probably looks like tremendous overkill at first (and it may be!),
since a it's possible to acheive a very reasonable "float slider" by
scaling input float values to some internal integer range for the QSlider,
and converting back to float when getting `value()`.  However, one still
runs into overflow limitations due to the internal integer model.

In order to circumvent them, one needs to reimplement more and more of
the attributes from QSliderPrivate in order to have the slider behave
like a native slider (with all of the proper signals and options).
So that's what `_GenericSlider` is below.

`_GenericRangeSlider` is a variant that expects `value()` and
`sliderPosition()` to be a sequence of scalars rather than a single
scalar (with one handle per item), and it forms the basis of
QRangeSlider.
"""

from typing import Generic, TypeVar

from .qtcompat import QtGui
from .qtcompat.QtCore import QEvent, QPoint, QPointF, QRect, Qt, Signal
from .qtcompat.QtWidgets import (
    QApplication,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QStylePainter,
)

_T = TypeVar("_T")

SC_NONE = QStyle.SubControl.SC_None
SC_HANDLE = QStyle.SubControl.SC_SliderHandle
SC_GROOVE = QStyle.SubControl.SC_SliderGroove
SC_TICKMARKS = QStyle.SubControl.SC_SliderTickmarks

CC_SLIDER = QStyle.ComplexControl.CC_Slider
QOVERFLOW = 2 ** 31 - 1


class _GenericSlider(QSlider, Generic[_T]):
    valueChanged = Signal(float)
    sliderMoved = Signal(float)
    rangeChanged = Signal(float, float)

    MAX_DISPLAY = 5000

    def __init__(self, *args, **kwargs) -> None:

        self._minimum = 0.0
        self._maximum = 99.0
        self._pageStep = 10.0
        self._value: _T = 0.0  # type: ignore
        self._position: _T = 0.0
        self._singleStep = 1.0
        self._offsetAccumulated = 0.0
        self._blocktracking = False
        self._tickInterval = 0.0
        self._pressedControl = SC_NONE
        self._hoverControl = SC_NONE
        self._hoverRect = QRect()
        self._clickOffset = 0.0

        # for keyboard nav
        self._repeatMultiplier = 1  # TODO
        # for wheel nav
        self._offset_accum = 0.0
        # fraction of total range to scroll when holding Ctrl while scrolling
        self._control_fraction = 0.04

        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_Hover)

    # ###############  QtOverrides  #######################

    def value(self) -> _T:  # type: ignore
        return self._value

    def setValue(self, value: _T) -> None:
        value = self._bound(value)
        if self._value == value and self._position == value:
            return
        self._value = value
        if self._position != value:
            self._setPosition(value)
            if self.isSliderDown():
                self.sliderMoved.emit(self.sliderPosition())
        self.sliderChange(self.SliderChange.SliderValueChange)
        self.valueChanged.emit(self.value())

    def sliderPosition(self) -> _T:  # type: ignore
        return self._position

    def setSliderPosition(self, pos: _T) -> None:
        position = self._bound(pos)
        if position == self._position:
            return
        self._setPosition(position)
        self._doSliderMove()

    def singleStep(self) -> float:  # type: ignore
        return self._singleStep

    def setSingleStep(self, step: float) -> None:
        if step != self._singleStep:
            self._setSteps(step, self._pageStep)

    def pageStep(self) -> float:  # type: ignore
        return self._pageStep

    def setPageStep(self, step: float) -> None:
        if step != self._pageStep:
            self._setSteps(self._singleStep, step)

    def minimum(self) -> float:  # type: ignore
        return self._minimum

    def setMinimum(self, min: float) -> None:
        self.setRange(min, max(self._maximum, min))

    def maximum(self) -> float:  # type: ignore
        return self._maximum

    def setMaximum(self, max: float) -> None:
        self.setRange(min(self._minimum, max), max)

    def setRange(self, min: float, max_: float) -> None:
        oldMin, self._minimum = self._minimum, float(min)
        oldMax, self._maximum = self._maximum, float(max(min, max_))

        if oldMin != self._minimum or oldMax != self._maximum:
            self.sliderChange(self.SliderRangeChange)
            self.rangeChanged.emit(self._minimum, self._maximum)
            self.setValue(self._value)  # re-bound

    def tickInterval(self) -> float:  # type: ignore
        return self._tickInterval

    def setTickInterval(self, ts: float) -> None:
        self._tickInterval = max(0.0, ts)
        self.update()

    def triggerAction(self, action: QSlider.SliderAction) -> None:
        self._blocktracking = True
        # other actions here
        # self.actionTriggered.emit(action)  # FIXME: type not working for all Qt
        self._blocktracking = False
        self.setValue(self._position)

    def initStyleOption(self, option: QStyleOptionSlider) -> None:
        option.initFrom(self)
        option.subControls = SC_NONE
        option.activeSubControls = SC_NONE
        option.orientation = self.orientation()
        option.tickPosition = self.tickPosition()
        option.upsideDown = (
            self.invertedAppearance() != (option.direction == Qt.RightToLeft)
            if self.orientation() == Qt.Horizontal
            else not self.invertedAppearance()
        )
        option.direction = Qt.LeftToRight  # we use the upsideDown option instead
        # option.sliderValue = self._value  # type: ignore
        # option.singleStep = self._singleStep  # type: ignore
        if self.orientation() == Qt.Horizontal:
            option.state |= QStyle.State_Horizontal

        # scale style option to integer space
        option.minimum = 0
        option.maximum = self.MAX_DISPLAY
        option.tickInterval = self._to_qinteger_space(self._tickInterval)
        option.pageStep = self._to_qinteger_space(self._pageStep)
        option.singleStep = self._to_qinteger_space(self._singleStep)
        self._fixStyleOption(option)

    def event(self, ev: QEvent) -> bool:
        if ev.type() == QEvent.WindowActivate:
            self.update()
        elif ev.type() in (QEvent.HoverEnter, QEvent.HoverMove):
            self._updateHoverControl(_event_position(ev))
        elif ev.type() == QEvent.HoverLeave:
            self._hoverControl = SC_NONE
            lastHoverRect, self._hoverRect = self._hoverRect, QRect()
            self.update(lastHoverRect)
        return super().event(ev)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._minimum == self._maximum or ev.buttons() ^ ev.button():
            ev.ignore()
            return

        ev.accept()

        pos = _event_position(ev)

        # If the mouse button used is allowed to set the value
        if ev.button() in (Qt.LeftButton, Qt.MiddleButton):
            self._updatePressedControl(pos)
            if self._pressedControl == SC_HANDLE:
                opt = self._styleOption
                sr = self.style().subControlRect(CC_SLIDER, opt, SC_HANDLE, self)
                offset = sr.center() - sr.topLeft()
                new_pos = self._pixelPosToRangeValue(self._pick(pos - offset))
                self.setSliderPosition(new_pos)
                self.triggerAction(QSlider.SliderMove)
                self.setRepeatAction(QSlider.SliderNoAction)

            self.update()
        # elif: deal with PageSetButtons
        else:
            ev.ignore()

        if self._pressedControl != SC_NONE:
            self.setRepeatAction(QSlider.SliderNoAction)
            self._setClickOffset(pos)
            self.update()
            self.setSliderDown(True)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        # TODO: add pixelMetric(QStyle::PM_MaximumDragDistance, &opt, this);
        if self._pressedControl == SC_NONE:
            ev.ignore()
            return
        ev.accept()
        pos = self._pick(_event_position(ev))
        newPosition = self._pixelPosToRangeValue(pos - self._clickOffset)
        self.setSliderPosition(newPosition)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._pressedControl == SC_NONE or ev.buttons():
            ev.ignore()
            return

        ev.accept()
        oldPressed = self._pressedControl
        self._pressedControl = SC_NONE
        self.setRepeatAction(QSlider.SliderNoAction)
        if oldPressed != SC_NONE:
            self.setSliderDown(False)
        self.update()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:

        e.ignore()
        vertical = bool(e.angleDelta().y())
        delta = e.angleDelta().y() if vertical else e.angleDelta().x()
        if e.inverted():
            delta *= -1

        orientation = Qt.Vertical if vertical else Qt.Horizontal
        if self._scrollByDelta(orientation, e.modifiers(), delta):
            e.accept()

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        painter = QStylePainter(self)
        opt = self._styleOption

        # draw groove and ticks
        opt.subControls = SC_GROOVE
        if opt.tickPosition != QSlider.NoTicks:
            opt.subControls |= SC_TICKMARKS
        painter.drawComplexControl(CC_SLIDER, opt)

        self._draw_handle(painter, opt)

    # ###############  Implementation Details  #######################

    def _type_cast(self, val):
        return val

    def _setPosition(self, val):
        self._position = val

    def _bound(self, value: _T) -> _T:
        return self._type_cast(max(self._minimum, min(self._maximum, value)))

    def _fixStyleOption(self, option):
        option.sliderPosition = self._to_qinteger_space(self._position - self._minimum)
        option.sliderValue = self._to_qinteger_space(self._value - self._minimum)

    def _to_qinteger_space(self, val, _max=None):
        _max = _max or self.MAX_DISPLAY
        return int(min(QOVERFLOW, val / (self._maximum - self._minimum) * _max))

    def _pick(self, pt: QPoint) -> int:
        return pt.x() if self.orientation() == Qt.Horizontal else pt.y()

    def _setSteps(self, single: float, page: float):
        self._singleStep = single
        self._pageStep = page
        self.sliderChange(QSlider.SliderStepsChange)

    def _doSliderMove(self):
        if not self.hasTracking():
            self.update()
        if self.isSliderDown():
            self.sliderMoved.emit(self.sliderPosition())
        if self.hasTracking() and not self._blocktracking:
            self.triggerAction(QSlider.SliderMove)

    @property
    def _styleOption(self):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        return opt

    def _updateHoverControl(self, pos: QPoint) -> bool:
        lastHoverRect = self._hoverRect
        lastHoverControl = self._hoverControl
        doesHover = self.testAttribute(Qt.WA_Hover)
        if lastHoverControl != self._newHoverControl(pos) and doesHover:
            self.update(lastHoverRect)
            self.update(self._hoverRect)
            return True
        return not doesHover

    def _newHoverControl(self, pos: QPoint) -> QStyle.SubControl:
        opt = self._styleOption
        opt.subControls = QStyle.SubControl.SC_All

        handleRect = self.style().subControlRect(CC_SLIDER, opt, SC_HANDLE, self)
        grooveRect = self.style().subControlRect(CC_SLIDER, opt, SC_GROOVE, self)
        tickmarksRect = self.style().subControlRect(CC_SLIDER, opt, SC_TICKMARKS, self)

        if handleRect.contains(pos):
            self._hoverRect = handleRect
            self._hoverControl = SC_HANDLE
        elif grooveRect.contains(pos):
            self._hoverRect = grooveRect
            self._hoverControl = SC_GROOVE
        elif tickmarksRect.contains(pos):
            self._hoverRect = tickmarksRect
            self._hoverControl = SC_TICKMARKS
        else:
            self._hoverRect = QRect()
            self._hoverControl = SC_NONE
        return self._hoverControl

    def _setClickOffset(self, pos: QPoint):
        hr = self.style().subControlRect(CC_SLIDER, self._styleOption, SC_HANDLE, self)
        self._clickOffset = self._pick(pos - hr.topLeft())

    def _updatePressedControl(self, pos: QPoint):
        self._pressedControl = SC_HANDLE

    def _draw_handle(self, painter, opt):
        opt.subControls = SC_HANDLE
        if self._pressedControl:
            opt.activeSubControls = self._pressedControl
            opt.state |= QStyle.State_Sunken
        else:
            opt.activeSubControls = self._hoverControl

        painter.drawComplexControl(CC_SLIDER, opt)

    # from QSliderPrivate.pixelPosToRangeValue
    def _pixelPosToRangeValue(self, pos: int) -> float:
        opt = self._styleOption

        gr = self.style().subControlRect(CC_SLIDER, opt, SC_GROOVE, self)
        sr = self.style().subControlRect(CC_SLIDER, opt, SC_HANDLE, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        return _sliderValueFromPosition(
            self._minimum,
            self._maximum,
            pos - sliderMin,
            sliderMax - sliderMin,
            opt.upsideDown,
        )

    def _scrollByDelta(self, orientation, modifiers, delta: int) -> bool:
        steps_to_scroll = 0.0
        pg_step = self._pageStep

        # in Qt scrolling to the right gives negative values.
        if orientation == Qt.Horizontal:
            delta *= -1
        offset = delta / 120
        if modifiers & Qt.ShiftModifier:
            # Scroll one page regardless of delta:
            steps_to_scroll = max(-pg_step, min(pg_step, offset * pg_step))
            self._offset_accum = 0
        elif modifiers & Qt.ControlModifier:
            _range = self._maximum - self._minimum
            steps_to_scroll = offset * _range * self._control_fraction
            self._offset_accum = 0
        else:
            # Calculate how many lines to scroll. Depending on what delta is (and
            # offset), we might end up with a fraction (e.g. scroll 1.3 lines). We can
            # only scroll whole lines, so we keep the reminder until next event.
            wheel_scroll_lines = QApplication.wheelScrollLines()
            steps_to_scrollF = wheel_scroll_lines * offset * self._effectiveSingleStep()
            # Check if wheel changed direction since last event:
            if self._offset_accum != 0 and (offset / self._offset_accum) < 0:
                self._offset_accum = 0

            self._offset_accum += steps_to_scrollF

            # Don't scroll more than one page in any case:
            steps_to_scroll = max(-pg_step, min(pg_step, self._offset_accum))
            self._offset_accum -= self._offset_accum

            if steps_to_scroll == 0:
                # We moved less than a line, but might still have accumulated partial
                # scroll, unless we already are at one of the ends.
                effective_offset = self._offset_accum
                if self.invertedControls():
                    effective_offset *= -1
                if self._has_scroll_space_left(effective_offset):
                    return True
                self._offset_accum = 0
                return False

        if self.invertedControls():
            steps_to_scroll *= -1

        prevValue = self._value
        self._execute_scroll(steps_to_scroll, modifiers)
        if prevValue == self._value:
            self._offset_accum = 0
            return False
        return True

    def _has_scroll_space_left(self, offset):
        return (offset > 0 and self._value < self._maximum) or (
            offset < 0 and self._value < self._minimum
        )

    def _execute_scroll(self, steps_to_scroll, modifiers):
        self._setPosition(self._bound(self._overflowSafeAdd(steps_to_scroll)))
        self.triggerAction(QSlider.SliderMove)

    def _effectiveSingleStep(self) -> float:
        return self._singleStep * self._repeatMultiplier

    def _overflowSafeAdd(self, add: float) -> float:
        newValue = self._value + add
        if add > 0 and newValue < self._value:
            newValue = self._maximum
        elif add < 0 and newValue > self._value:
            newValue = self._minimum
        return newValue

    # def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
    #     return  # TODO


def _event_position(ev: QEvent) -> QPoint:
    # safe for Qt6, Qt5, and hoverEvent
    evp = getattr(ev, "position", getattr(ev, "pos", None))
    pos = evp() if evp else QPoint()
    if isinstance(pos, QPointF):
        pos = pos.toPoint()
    return pos


def _sliderValueFromPosition(
    min: float, max: float, position: int, span: int, upsideDown: bool = False
) -> float:
    """Converts the given pixel `position` to a value.

    0 maps to the `min` parameter, `span` maps to `max` and other values are
    distributed evenly in-between.

    By default, this function assumes that the maximum value is on the right
    for horizontal items and on the bottom for vertical items. Set the
    `upsideDown` parameter to True to reverse this behavior.
    """

    if span <= 0 or position <= 0:
        return max if upsideDown else min
    if position >= span:
        return min if upsideDown else max
    range = max - min
    tmp = min + position * range / span
    return max - tmp if upsideDown else tmp + min
