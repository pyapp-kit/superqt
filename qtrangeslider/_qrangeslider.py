import textwrap
from collections import abc
from typing import List, Sequence, Tuple

from ._style import RangeSliderStyle, update_styles_from_stylesheet
from .qtcompat import QtGui
from .qtcompat.QtCore import (
    Property,
    QEvent,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    Qt,
    Signal,
)
from .qtcompat.QtWidgets import (
    QApplication,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QStylePainter,
)

ControlType = Tuple[str, int]


class QRangeSlider(QSlider):
    """MultiHandle Range Slider widget.

    Same API as QSlider, but `value`, `setValue`, `sliderPosition`, and
    `setSliderPosition` are all sequences of integers.

    The `valueChanged` and `sliderMoved` signals also both emit a tuple of
    integers.
    """

    # Emitted when the slider value has changed, with the new slider values
    valueChanged = Signal(tuple)

    # Emitted when sliderDown is true and the slider moves
    # This usually happens when the user is dragging the slider
    # The value is the positions of *all* handles.
    sliderMoved = Signal(tuple)

    _NULL_CTRL = ("None", -1)

    def __init__(self, *args):
        super().__init__(*args)

        # list of values
        self._value: List[int] = [20, 80]

        # list of current positions of each handle. same length as _value
        # If tracking is enabled (the default) this will be identical to _value
        self._position: List[int] = [20, 80]
        self._pressedControl: ControlType = self._NULL_CTRL
        self._hoverControl: ControlType = self._NULL_CTRL

        # whether bar length is constant when dragging the bar
        # if False, the bar can shorten when dragged beyond min/max
        self._bar_is_rigid = True
        # whether clicking on the bar moves all handles, or just the nearest handle
        self._bar_moves_all = True
        self._should_draw_bar = True

        # for keyboard nav
        self._repeatMultiplier = 1  # TODO
        # for wheel nav
        self._offset_accum = 0

        # color
        self._style = RangeSliderStyle()
        self.setStyleSheet("")

    # ###############  Public API  #######################

    def setStyleSheet(self, styleSheet: str) -> None:
        # sub-page styles render on top of the lower sliders and don't work here.
        override = f"""
            \n{type(self).__name__}::sub-page:horizontal {{background: none}}
            \n{type(self).__name__}::sub-page:vertical {{background: none}}
        """
        return super().setStyleSheet(styleSheet + override)

    def value(self) -> Tuple[int, ...]:
        """Get current value of the widget as a tuple of integers."""
        return tuple(self._value)

    def setValue(self, val: Sequence[int]) -> None:
        """Set current value of the widget with a sequence of integers.

        The number of handles will be equal to the length of the sequence
        """
        if not isinstance(val, abc.Sequence) and len(val) >= 2:
            raise ValueError("value must be iterable of len >= 2")
        val = [self._min_max_bound(v) for v in val]
        if self._value == val and self._position == val:
            return

        self._value[:] = val[:]
        if self._position != val:
            self._position = val
            if self.isSliderDown():
                self.sliderMoved.emit(tuple(self._position))

        self.sliderChange(QSlider.SliderValueChange)
        self.valueChanged.emit(tuple(self._value))

    def sliderPosition(self) -> Tuple[int, ...]:
        """Get current value of the widget as a tuple of integers.

        If tracking is enabled (the default) this will be identical to value().
        """
        return tuple(self._position)

    def setSliderPosition(self, val: Sequence[int]) -> None:
        """Set current position of the handles with a sequence of integers.

        The sequence must have the same length as `value()`.
        """
        if len(val) != len(self.value()):
            raise ValueError(
                f"'sliderPosition' must have length of 'value()' ({len(self.value())})"
            )

        for i, v in enumerate(val):
            self._setSliderPositionAt(i, v, _update=i == len(val) - 1)

    def barIsRigid(self) -> bool:
        """Whether bar length is constant when dragging the bar.

        If False, the bar can shorten when dragged beyond min/max. Default is True.
        """
        return self._bar_is_rigid

    def setBarIsRigid(self, val: bool = True) -> None:
        """Whether bar length is constant when dragging the bar.

        If False, the bar can shorten when dragged beyond min/max. Default is True.
        """
        self._bar_is_rigid = bool(val)

    def barMovesAllHandles(self) -> bool:
        """Whether clicking on the bar moves all handles (default), or just the nearest."""
        return self._bar_moves_all

    def setBarMovesAllHandles(self, val: bool = True) -> None:
        """Whether clicking on the bar moves all handles (default), or just the nearest."""
        self._bar_moves_all = bool(val)

    def barIsVisible(self) -> bool:
        """Whether to show the bar between the first and last handle."""
        return self._should_draw_bar

    def setBarVisible(self, val: bool = True) -> None:
        """Whether to show the bar between the first and last handle."""
        self._should_draw_bar = bool(val)

    def hideBar(self) -> None:
        self.setBarVisible(False)

    def showBar(self) -> None:
        self.setBarVisible(True)

    # ###############  Implementation Details  #######################

    def _setSliderPositionAt(self, index: int, pos: int, _update=True) -> None:
        pos = self._min_max_bound(pos)
        # prevent sliders from moving beyond their neighbors
        pos = self._neighbor_bound(pos, index, self._position)
        if pos == self._position[index]:
            return
        self._position[index] = pos
        if _update:
            if not self.hasTracking():
                self.update()
            if self.isSliderDown():
                self.sliderMoved.emit(tuple(self._position))
            if self.hasTracking():
                self.triggerAction(QSlider.SliderMove)

    def _offsetAllPositions(self, offset: int, ref=None) -> None:
        if ref is None:
            ref = self._position
        _new = [i - offset for i in ref]
        if self._bar_is_rigid:
            # FIXME: if there is an overflow ... it should still hit the edge.
            if all(self.minimum() <= i <= self.maximum() for i in _new):
                self.setSliderPosition(_new)
        else:
            self.setSliderPosition(_new)

    def _getStyleOption(self) -> QStyleOptionSlider:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt.sliderValue = 0
        opt.sliderPosition = 0
        return opt

    def _getBarColor(self):
        return self._style.brush_active or QtGui.QColor()

    def _setBarColor(self, color):
        self._style.brush_active = color

    barColor = Property(QtGui.QColor, _getBarColor, _setBarColor)

    def _drawBar(self, painter: QStylePainter, opt: QStyleOptionSlider):

        brush = self._style.brush(opt)

        r_bar = self._barRect(opt)
        if isinstance(brush, QtGui.QGradient):
            brush.setStart(r_bar.topLeft())
            brush.setFinalStop(r_bar.bottomRight())

        painter.setPen(self._style.pen(opt))
        painter.setBrush(brush)
        painter.drawRect(r_bar)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """Paint the slider."""
        # initialize painter and options
        painter = QStylePainter(self)
        opt = self._getStyleOption()

        # draw groove and ticks
        opt.subControls = QStyle.SC_SliderGroove | QStyle.SC_SliderTickmarks
        painter.drawComplexControl(QStyle.CC_Slider, opt)

        if self._should_draw_bar:
            self._drawBar(painter, opt)

        # draw handles
        opt.subControls = QStyle.SC_SliderHandle
        hidx = -1
        pidx = -1
        if self._pressedControl[0] == "handle":
            pidx = self._pressedControl[1]
        elif self._hoverControl[0] == "handle":
            hidx = self._hoverControl[1]
        for idx, pos in enumerate(self._position):
            opt.sliderPosition = pos
            if idx == pidx:  # make pressed handles appear sunken
                opt.state |= QStyle.State_Sunken
            else:
                opt.state = opt.state & ~QStyle.State_Sunken
            if idx == hidx:
                opt.activeSubControls = QStyle.SC_SliderHandle
            else:
                opt.activeSubControls = QStyle.SC_None
            painter.drawComplexControl(QStyle.CC_Slider, opt)

    def event(self, ev: QEvent) -> bool:
        if ev.type() == QEvent.WindowActivate:
            self.update()
        if ev.type() == QEvent.StyleChange:
            update_styles_from_stylesheet(self)
        if ev.type() in (QEvent.HoverEnter, QEvent.HoverLeave, QEvent.HoverMove):
            old_hover = self._hoverControl
            self._hoverControl = self._getControlAtPos(ev.pos())
            if self._hoverControl != old_hover:
                self.update()  # TODO: restrict to the rect of old_hover
        return super().event(ev)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.minimum() == self.maximum() or ev.buttons() ^ ev.button():
            ev.ignore()
            return

        ev.accept()
        # FIXME: why not working on other styles?
        # set_buttons = self.style().styleHint(QStyle.SH_Slider_AbsoluteSetButtons)
        set_buttons = Qt.LeftButton | Qt.MiddleButton

        # If the mouse button used is allowed to set the value
        if ev.buttons() & set_buttons == ev.button():
            opt = self._getStyleOption()

            self._pressedControl = self._getControlAtPos(ev.pos(), opt, True)

            if self._pressedControl[0] == "handle":
                offset = self._handle_offset(opt)
                new_pos = self._pixelPosToRangeValue(self._pick(ev.pos() - offset))
                self._setSliderPositionAt(self._pressedControl[1], new_pos)
                self.triggerAction(QSlider.SliderMove)
                self.setRepeatAction(QSlider.SliderNoAction)
            self.update()

        if self._pressedControl[0] == "handle":
            self.setRepeatAction(QSlider.SliderNoAction)  # why again?
            sr = self._handleRects(opt, self._pressedControl[1])
            self._clickOffset = self._pick(ev.pos() - sr.topLeft())
            self.update()
            self.setSliderDown(True)
        elif self._pressedControl[0] == "bar":
            self.setRepeatAction(QSlider.SliderNoAction)  # why again?
            self._clickOffset = self._pixelPosToRangeValue(self._pick(ev.pos()))
            self._sldPosAtPress = tuple(self._position)
            self.update()
            self.setSliderDown(True)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        # TODO: add pixelMetric(QStyle::PM_MaximumDragDistance, &opt, this);
        if self._pressedControl[0] == "handle":
            ev.accept()
            new = self._pixelPosToRangeValue(self._pick(ev.pos()) - self._clickOffset)
            self._setSliderPositionAt(self._pressedControl[1], new)
        elif self._pressedControl[0] == "bar":
            ev.accept()
            delta = self._clickOffset - self._pixelPosToRangeValue(self._pick(ev.pos()))
            self._offsetAllPositions(delta, self._sldPosAtPress)
        else:
            ev.ignore()
            return

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._pressedControl[0] == "None" or ev.buttons():
            ev.ignore()
            return
        ev.accept()
        old_pressed = self._pressedControl
        self._pressedControl = self._NULL_CTRL
        self.setRepeatAction(QSlider.SliderNoAction)
        if old_pressed[0] in ("handle", "bar"):
            self.setSliderDown(False)
        self.update()  # TODO: restrict to the rect of old_pressed

    def triggerAction(self, action: QSlider.SliderAction) -> None:
        super().triggerAction(action)  # TODO: probably need to override.
        self.setValue(self._position)

    def setRange(self, min: int, max: int) -> None:
        super().setRange(min, max)
        self.setValue(self._value)  # re-bound

    def _handleRects(self, opt: QStyleOptionSlider, handle_index: int = None) -> QRect:
        """Return the QRect for all handles."""
        style = self.style().proxy()

        if handle_index is not None:  # get specific handle rect
            opt.sliderPosition = self._position[handle_index]
            return style.subControlRect(
                QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
            )
        else:
            rects = []
            for p in self._position:
                opt.sliderPosition = p
                r = style.subControlRect(
                    QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
                )
                rects.append(r)
            return rects

    def _grooveRect(self, opt: QStyleOptionSlider) -> QRect:
        """Return the QRect for the slider groove."""
        style = self.style().proxy()
        return style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)

    def _barRect(self, opt: QStyleOptionSlider, r_groove: QRect = None) -> QRect:
        """Return the QRect for the bar between the outer handles."""
        if r_groove is None:
            r_groove = self._grooveRect(opt)
        r_bar = QRectF(r_groove)
        hdl_low, *_, hdl_high = self._handleRects(opt)

        thickness = self._style.thickness(opt)
        offset = self._style.offset(opt)

        if opt.orientation == Qt.Horizontal:
            r_bar.setTop(r_bar.center().y() - thickness / 2 + offset)
            r_bar.setHeight(thickness)
            r_bar.setLeft(hdl_low.center().x())
            r_bar.setRight(hdl_high.center().x())
        else:
            r_bar.setLeft(r_bar.center().x() - thickness / 2 + offset)
            r_bar.setWidth(thickness)
            r_bar.setBottom(hdl_low.center().y())
            r_bar.setTop(hdl_high.center().y())

        return r_bar

    def _getControlAtPos(
        self, pos: QPoint, opt: QStyleOptionSlider = None, closest_handle=False
    ) -> ControlType:
        """Update self._pressedControl based on ev.pos()."""
        if not opt:
            opt = self._getStyleOption()

        event_position = self._pick(pos)
        bar_idx = 0
        hdl_idx = 0
        dist = float("inf")

        if isinstance(pos, QPointF):
            pos = QPoint(pos.x(), pos.y())
        # TODO: this should be reversed, to prefer higher value handles
        for i, hdl in enumerate(self._handleRects(opt)):
            if hdl.contains(pos):
                return ("handle", i)  # TODO: use enum for 'handle'
            hdl_center = self._pick(hdl.center())
            abs_dist = abs(event_position - hdl_center)
            if abs_dist < dist:
                dist = abs_dist
                hdl_idx = i
            if event_position > hdl_center:
                bar_idx += 1
        else:
            if closest_handle:
                if bar_idx == 0:
                    # the click was below the minimum slider
                    return ("handle", 0)
                elif bar_idx == len(self._position):
                    # the click was above the maximum slider
                    return ("handle", len(self._position) - 1)
            if self._bar_moves_all:
                # the click was in an internal segment
                return ("bar", bar_idx)
            elif closest_handle:
                return ("handle", hdl_idx)

        return self._NULL_CTRL

    def _handle_offset(self, opt: QStyleOptionSlider) -> QPoint:
        # to take half of the slider off for the setSliderPosition call we use the
        # center - topLeft
        handle_rect = self._handleRects(opt, 0)
        return handle_rect.center() - handle_rect.topLeft()

    # from QSliderPrivate::pixelPosToRangeValue
    def _pixelPosToRangeValue(self, pos: int, opt: QStyleOptionSlider = None) -> int:
        if not opt:
            opt = self._getStyleOption()

        groove_rect = self._grooveRect(opt)
        handle_rect = self._handleRects(opt, 0)
        if self.orientation() == Qt.Horizontal:
            sliderLength = handle_rect.width()
            sliderMin = groove_rect.x()
            sliderMax = groove_rect.right() - sliderLength + 1
        else:
            sliderLength = handle_rect.height()
            sliderMin = groove_rect.y()
            sliderMax = groove_rect.bottom() - sliderLength + 1
        return QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            pos - sliderMin,
            sliderMax - sliderMin,
            opt.upsideDown,
        )

    def _pick(self, pt: QPoint) -> int:
        return pt.x() if self.orientation() == Qt.Horizontal else pt.y()

    def _min_max_bound(self, val: int) -> int:
        return _bound(self.minimum(), self.maximum(), val)

    def _neighbor_bound(self, val: int, index: int, _lst: List[int]) -> int:
        # make sure we don't go lower than any preceding index:
        if index > 0:
            val = max(_lst[index - 1], val)
        # make sure we don't go higher than any following index:
        if index < len(_lst) - 1:
            val = min(_lst[index + 1], val)
        return val

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        e.ignore()
        vertical = bool(e.angleDelta().y())
        delta = e.angleDelta().y() if vertical else e.angleDelta().x()
        if e.inverted():
            delta *= -1

        orientation = Qt.Vertical if vertical else Qt.Horizontal
        if self._scrollByDelta(orientation, e.modifiers(), delta):
            e.accept()

    def _scrollByDelta(
        self, orientation, modifiers: Qt.KeyboardModifiers, delta: int
    ) -> bool:
        steps_to_scroll = 0
        pg_step = self.pageStep()

        # in Qt scrolling to the right gives negative values.
        if orientation == Qt.Horizontal:
            delta *= -1
        offset = delta / 120
        if modifiers & Qt.ControlModifier or modifiers & Qt.ShiftModifier:
            # Scroll one page regardless of delta:
            steps_to_scroll = _bound(-pg_step, pg_step, int(offset * pg_step))
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
            steps_to_scroll = _bound(-pg_step, pg_step, int(self._offset_accum))

            self._offset_accum -= int(self._offset_accum)

            if steps_to_scroll == 0:
                # We moved less than a line, but might still have accumulated partial
                # scroll, unless we already are at one of the ends.
                effective_offset = self._offset_accum
                if self.invertedControls():
                    effective_offset *= -1
                if effective_offset > 0 and max(self._value) < self.maximum():
                    return True
                if effective_offset < 0 and min(self._value) < self.minimum():
                    return True
                self._offset_accum = 0
                return False

        if self.invertedControls():
            steps_to_scroll *= -1

        _prev_value = self.value()

        self._offsetAllPositions(-steps_to_scroll)
        self.triggerAction(QSlider.SliderMove)

        if _prev_value == self.value():
            self._offset_accum = 0
            return False
        return True

    def _effectiveSingleStep(self) -> int:
        return self.singleStep() * self._repeatMultiplier

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        return  # TODO


def _bound(min_: int, max_: int, value: int) -> int:
    """Return value bounded by min_ and max_."""
    return max(min_, min(max_, value))


QRangeSlider.__doc__ += "\n" + textwrap.indent(QSlider.__doc__, "    ")
