import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

from qtpy import QtGui
from qtpy.QtCore import (
    Property,
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSizeF,
    Qt,
    Signal,
    qVersion,
)
from qtpy.QtGui import (
    QBrush,
    QColor,
    QGradient,
    QImage,
    QLinearGradient,
    QPainter,
    QPalette,
    QRadialGradient,
)
from qtpy.QtWidgets import (
    QApplication,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QStylePainter,
)

from ._generic_slider import (
    CC_SLIDER,
    MONTEREY_SLIDER_STYLES_FIX,
    SC_GROOVE,
    SC_HANDLE,
    SC_NONE,
    SC_TICKMARKS,
    _GenericSlider,
)

_T = TypeVar("_T")


SC_BAR = QStyle.SubControl.SC_ScrollBarSubPage
# whether Qt draws style sheets' sub-page and add-page with each handle (and so over
# the bar), as it did up to 6.10.0 (https://bugreports.qt.io/browse/QTBUG-141157)
_QT = tuple(int(n) for n in re.findall(r"\d+", qVersion())[:3])
_PAGES_WITH_EACH_HANDLE = _QT < (6, 10, 1)


class _GenericRangeSlider(_GenericSlider):
    """MultiHandle Range Slider widget.

    Same API as QSlider, but `value`, `setValue`, `sliderPosition`, and
    `setSliderPosition` are all sequences of integers.

    The `valueChanged` and `sliderMoved` signals also both emit a tuple of
    integers.
    """

    # Emitted when the slider value has changed, with the new slider values
    valuesChanged = Signal(tuple)
    # this is just a hack to allow napari v0.4.19 tests to pass)
    # since it used the presence of this private signal as a duck-typing check.
    _valuesChanged = valuesChanged

    # Emitted when sliderDown is true and the slider moves
    # This usually happens when the user is dragging the slider
    # The value is the positions of *all* handles.
    slidersMoved = Signal(tuple)

    def __init__(self, *args, **kwargs):
        self._style = _BarColors()
        self._macpatch = False  # (whether `applyMacStylePatch` was called)

        super().__init__(*args, **kwargs)

        # list of values
        self._value: list[_T] = [20, 80]

        # list of current positions of each handle. same length as _value
        # If tracking is enabled (the default) this will be identical to _value
        self._position: list[_T] = [20, 80]

        # which handle is being pressed/hovered
        self._pressedIndex = 0
        self._hoverIndex = 0

        # whether bar length is constant when dragging the bar
        # if False, the bar can shorten when dragged beyond min/max
        self._bar_is_rigid = True
        # whether clicking on the bar moves all handles, or just the nearest handle
        self._bar_moves_all = True
        self._should_draw_bar = True

        # color

        self.setStyleSheet("")

    def _rename_signals(self) -> None:
        self.valueChanged = self.valuesChanged
        self.sliderMoved = self.slidersMoved

    # ###############  New Public API  #######################

    def barIsRigid(self) -> bool:
        """Whether bar length is constant when dragging the bar.

        If `False`, the bar can shorten when dragged beyond min/max. Default is `True`.
        """
        return self._bar_is_rigid

    def setBarIsRigid(self, val: bool = True) -> None:
        """Whether bar length is constant when dragging the bar.

        If `False`, the bar can shorten when dragged beyond min/max. Default is `True`.
        """
        self._bar_is_rigid = bool(val)

    def barMovesAllHandles(self) -> bool:
        """Whether clicking on the bar moves all handles, or just the nearest."""
        return self._bar_moves_all

    def setBarMovesAllHandles(self, val: bool = True) -> None:
        """Whether clicking on the bar moves all handles, or just the nearest."""
        self._bar_moves_all = bool(val)

    def barIsVisible(self) -> bool:
        """Whether to show the bar between the first and last handle."""
        return self._should_draw_bar

    def setBarVisible(self, val: bool = True) -> None:
        """Whether to show the bar between the first and last handle."""
        self._should_draw_bar = bool(val)

    def hideBar(self) -> None:
        """Hide the bar between the first and last handle."""
        self.setBarVisible(False)

    def showBar(self) -> None:
        """Show the bar between the first and last handle."""
        self.setBarVisible(True)

    def applyMacStylePatch(self) -> None:
        """Apply a QSS patch to fix sliders on macos>=12 with QT < 6.

        see [FAQ](../faq.md#sliders-not-dragging-properly-on-macos-12) for more details.
        """
        super().applyMacStylePatch()
        self._macpatch = True

    # ###############  QtOverrides  #######################

    def value(self) -> tuple[_T, ...]:
        """Get current value of the widget as a tuple of integers."""
        return tuple(self._value)

    def sliderPosition(self):
        """Get current value of the widget as a tuple of integers.

        If tracking is enabled (the default) this will be identical to value().
        """
        return tuple(float(i) for i in self._position)

    def setSliderPosition(  # type: ignore
        self,
        pos: float | Sequence[float],
        index: int | None = None,
        *,
        reversed: bool = False,
    ) -> None:
        """Set current position of the handles with a sequence of integers.

        Parameters
        ----------
        pos : Union[float, Sequence[float]]
            The new position of the slider handle(s). If a sequence, it must have the
            same length as `value()`. If it is a scalar, index will be used to set the
            position of the handle at that index.
        index : int | None
            The index of the handle to set the position of. If None, the "pressedIndex"
            will be used.
        reversed : bool
            Order in which to set the positions.  Can be useful when setting multiple
            positions, to avoid intermediate overlapping values.
        """
        if isinstance(pos, (list, tuple)):
            val_len = len(self.value())
            if len(pos) != val_len:
                msg = f"'sliderPosition' must have same length as 'value()' ({val_len})"
                raise ValueError(msg)
            pairs = list(enumerate(pos))
        else:
            pairs = [(self._pressedIndex if index is None else index, pos)]

        if reversed:
            pairs = pairs[::-1]

        for idx, position in pairs:
            self._position[idx] = self._bound(position, idx)

        self._doSliderMove()

    def setStyleSheet(self, styleSheet: str) -> None:
        return super().setStyleSheet(self._patch_style(styleSheet))

    def _patch_style(self, style: str):
        """Override to patch style options before painting."""
        if self._macpatch and not style:
            style = MONTEREY_SLIDER_STYLES_FIX
        return style

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self._pressedControl == SC_BAR:
            ev.accept()
            delta = self._clickOffset - self._pixelPosToRangeValue(
                self._pick(self._event_position(ev))
            )
            self._offsetAllPositions(-delta, self._sldPosAtPress)
        else:
            super().mouseMoveEvent(ev)

    def _event_position(self, event):
        # API changes between PyQt5 (.pos()) and PyQt6 (.position())
        return event.pos() if hasattr(event, "pos") else event.position()

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        painter = QStylePainter(self)
        opt = self._styleOption

        bar = self._barOption(opt, _ratio(painter))
        groove = self._drawGroove(painter, bar)
        if self._should_draw_bar:
            self._drawBar(painter, opt, bar, groove)
        self._drawTicks(painter, opt)  # (after the bar, which could cover them)
        self._draw_handle(painter, opt)

    # ###############  Implementation Details  #######################

    def _setPosition(self, val):
        self._position = list(val)

    def _bound(self, value, index=None):
        if isinstance(value, (list, tuple)):
            return [self._bound(v) for v in value]
        pos = super()._bound(value)
        if index is not None:
            pos = self._neighbor_bound(pos, index)
        return self._type_cast(pos)

    def _neighbor_bound(self, val, index):
        # make sure we don't go lower than any preceding index:
        min_dist = self.singleStep()
        _lst = self._position
        if index > 0:
            val = max(_lst[index - 1] + min_dist, val)
        # make sure we don't go higher than any following index:
        if index < (len(_lst) - 1):
            val = min(_lst[index + 1] - min_dist, val)
        return val

    def _getBarColor(self) -> QBrush:
        opt = self._styleOption
        return self._barBrush(opt) or self._fillBrush(opt)

    def _setBarColor(self, color: Any) -> None:
        self._style.brush_active = color
        self.update()

    barColor = Property(QtGui.QBrush, _getBarColor, _setBarColor)
    """The color of the bar between the first and last handle."""

    def _offsetAllPositions(self, offset: float, ref=None) -> None:
        if ref is None:
            ref = self._position
        if self._bar_is_rigid:
            # NOTE: This assumes monotonically increasing slider positions
            if offset > 0 and ref[-1] + offset > self.maximum():
                offset = self.maximum() - ref[-1]
            elif ref[0] + offset < self.minimum():
                offset = self.minimum() - ref[0]
        self.setSliderPosition([i + offset for i in ref], reversed=offset > 0)

    def _fixStyleOption(self, option):
        pass

    @property
    def _optSliderPositions(self):
        return [self._to_qinteger_space(p - self._minimum) for p in self._position]

    # SubControl Positions

    def _handleRect(
        self, handle_index: int, opt: QStyleOptionSlider | None = None
    ) -> QRect:
        """Return the QRect for all handles."""
        opt = opt or self._styleOption
        opt.sliderPosition = self._optSliderPositions[handle_index]
        return self.style().subControlRect(CC_SLIDER, opt, SC_HANDLE, self)

    # Painting

    def _drawGroove(self, painter: QStylePainter, bar: QStyleOptionSlider) -> QImage:
        """Draw the style's groove, without any fill; return it.

        (As the bar is drawn, by `bar`: see `_barOption`.) Styles fill the groove
        from the minimum up to the handle, and some do even with the handle at the
        minimum (e.g. Windows 11). Drawn upside down, that bit of fill is at the
        other end: so the groove under a handle at the minimum comes from the slider
        drawn upside down. But some styles fill from the same end either way:
        Windows 11 up to Qt 6.10.0, and style sheets, whose sub-page is always at the
        left or top, once Qt draws it with the groove
        (https://bugreports.qt.io/browse/QTBUG-141608). Then that part of the groove
        is the mirror image of its other end, in the colors next to it.
        """
        horizontal = bar.orientation == Qt.Orientation.Horizontal
        ratio = _ratio(painter)
        groove = self._grooveImage(bar, bar.minimum, ratio)
        flipped = QStyleOptionSlider(bar)
        flipped.upsideDown = not bar.upsideDown
        other = self._grooveImage(flipped, bar.minimum, ratio)

        option = QStyleOptionSlider(bar)
        option.sliderPosition = option.minimum
        start = self.style().subControlRect(CC_SLIDER, option, SC_HANDLE, self)
        option.sliderPosition = option.maximum
        end = self.style().subControlRect(CC_SLIDER, option, SC_HANDLE, self)
        # (from the slider's end with the minimum to the far side of a handle at the
        # minimum; and the groove between that and the other)
        under, between = QRect(self.rect()), QRect(self.rect())
        if horizontal:
            under.setRight(start.right())
            between.setLeft(start.right() + 1)
            between.setRight(end.left() - 1)
        elif bar.upsideDown:  # (the minimum at the bottom)
            under.setTop(start.top())
            between.setTop(end.bottom() + 1)
            between.setBottom(start.top() - 1)
        else:
            under.setBottom(start.bottom())
            between.setTop(start.bottom() + 1)
            between.setBottom(end.top() - 1)

        mix = QPainter(groove)
        mix.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        mix.setClipRect(under)
        if _crop(groove, between) == _crop(other, between):
            mix.drawImage(0, 0, other)
        else:  # (the mirror image of the other end, then the colors next to it)
            mirror = groove.copy()
            next_to = QRectF(QPointF(between.topLeft()) * ratio, QSizeF(between.size()))
            next_to.setSize(next_to.size() * ratio)
            if horizontal:  # (its first column, or row: next to that part)
                mix.translate(self.width(), 0)
                mix.scale(-1, 1)
                next_to.setWidth(1)
            else:
                mix.translate(0, self.height())
                mix.scale(1, -1)
                if bar.upsideDown:
                    next_to.setTop(next_to.bottom() - 1)
                else:
                    next_to.setHeight(1)
            mix.drawImage(0, 0, mirror)
            mix.resetTransform()
            mix.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            mix.drawImage(QRectF(under), mirror, next_to)
        mix.end()
        painter.drawImage(0, 0, groove)
        return groove

    def _drawBar(
        self,
        painter: QStylePainter,
        opt: QStyleOptionSlider,
        bar: QStyleOptionSlider,
        groove: QImage,
    ) -> None:
        """Draw the bar between the outer handles, in the style's groove (`groove`).

        Without a `barColor`, it's the style's own fill of the groove, if it has one
        (as on macOS, with Fusion and Windows 11, or a style sheet's sub-page): what
        the slider drawn as the bar (`bar`, see `_barOption`) fills, up to the
        handle, whichever way this one goes. Otherwise, it's a solid bar as thick as
        the groove (and its fill), in the `barColor` (as is, in any state, like a
        style sheet's colors) or the style's fill color.
        """
        horizontal = opt.orientation == Qt.Orientation.Horizontal
        ends = [self._handleRect(i, opt).center() for i in (0, -1)]
        span = QRect(self.rect())  # (the part of the slider between the outer handles)
        if horizontal:
            span.setLeft(min(p.x() for p in ends))
            span.setRight(max(p.x() for p in ends))
        else:
            span.setTop(min(p.y() for p in ends))
            span.setBottom(max(p.y() for p in ends))

        # The groove, filled all along (as the bar is drawn), with a handle: up to
        # 6.12.0, style sheets only draw pages with one. That handle, at the
        # maximum, isn't part of the bar.
        option = QStyleOptionSlider(bar)
        option.sliderPosition = option.maximum
        handle = self.style().subControlRect(CC_SLIDER, option, SC_HANDLE, self)
        inner = _apart(span, handle, horizontal)
        if inner.isEmpty():  # (the bar is under the handles)
            return
        empty = _crop(groove, inner)
        ratio = _ratio(painter)
        if (brush := self._barBrush(opt)) is None:
            filled = self._grooveImage(option, option.maximum, ratio, handle=True)
            filled = _crop(filled, inner)
            if filled != empty:
                painter.drawImage(inner.topLeft(), filled)
                return
            bounds = _bounds(empty)
        else:  # (filled without the handle, which may reach past its rect)
            filled = self._grooveImage(option, option.maximum, ratio)
            bounds = _bounds(_crop(filled, inner))
        if bounds.isEmpty():  # (the style draws no groove)
            painter.fillRect(self._plainBar(opt, span), brush or self._fillBrush(opt))
        else:  # (even if the groove is hollow, or its fill translucent)
            bounds.translate(QPointF(inner.topLeft()))
            rect = QRectF(span)
            if horizontal:
                rect.setTop(bounds.top())
                rect.setBottom(bounds.bottom())
            else:
                rect.setLeft(bounds.left())
                rect.setRight(bounds.right())
            painter.fillRect(rect, brush or self._fillBrush(opt))

    def _barOption(self, opt: QStyleOptionSlider, ratio: float) -> QStyleOptionSlider:
        """A copy of `opt`, as the bar is drawn: with the minimum at the left, or top.

        So in either orientation, the bar is the part of the groove before a handle,
        where style sheets draw their sub-page. But up to Qt 6.10.0, Windows 11 fills
        vertical grooves from the bottom up to the handle, whichever way the slider
        goes: then the bar is drawn from the bottom. (`ratio`: the painter's.)
        """
        option = QStyleOptionSlider(opt)
        option.upsideDown = False
        if not _PAGES_WITH_EACH_HANDLE or opt.orientation == Qt.Orientation.Horizontal:
            return option
        # (Style sheets then draw no pages with the groove alone: if, between handles
        # at both ends, it's not the same either way, its fill is by position.)
        flipped = QStyleOptionSlider(option)
        flipped.upsideDown = True
        top, bottom = QStyleOptionSlider(option), QStyleOptionSlider(flipped)
        top.sliderPosition = bottom.sliderPosition = opt.minimum
        top_end = self.style().subControlRect(CC_SLIDER, top, SC_HANDLE, self)
        bottom_end = self.style().subControlRect(CC_SLIDER, bottom, SC_HANDLE, self)
        between = QRect(self.rect())
        between.setTop(top_end.bottom() + 1)
        between.setBottom(bottom_end.top() - 1)
        groove = self._grooveImage(option, opt.minimum, ratio)
        other = self._grooveImage(flipped, opt.minimum, ratio)
        if _crop(groove, between) != _crop(other, between):
            option.upsideDown = True
        return option

    def _drawTicks(self, painter: QStylePainter, opt: QStyleOptionSlider) -> None:
        if opt.tickPosition != QSlider.TickPosition.NoTicks:
            opt.subControls = SC_TICKMARKS
            painter.drawComplexControl(CC_SLIDER, opt)
            self._draw_qss_ticks(painter, opt)

    def _plainBar(self, opt: QStyleOptionSlider, span: QRect) -> QRectF:
        """A 4px bar across `span`, centered on the style's groove."""
        groove = self.style().subControlRect(CC_SLIDER, opt, SC_GROOVE, self)
        bar = QRectF(span)
        if opt.orientation == Qt.Orientation.Horizontal:
            bar.setTop(groove.center().y() - 2)
            bar.setHeight(4)
        else:
            bar.setLeft(groove.center().x() - 2)
            bar.setWidth(4)
        return bar

    def _grooveImage(
        self,
        opt: QStyleOptionSlider,
        position: int,
        ratio: float,
        style: QStyle | None = None,
        handle: bool = False,
    ) -> QImage:
        """The style's groove (and `handle`), filled up to `position`."""
        option = QStyleOptionSlider(opt)
        option.subControls = SC_GROOVE | SC_HANDLE if handle else SC_GROOVE
        option.sliderPosition = position
        return self._sliderImage(option, ratio, style)

    def _sliderImage(
        self, opt: QStyleOptionSlider, ratio: float, style: QStyle | None = None
    ) -> QImage:
        """What the style draws for `opt`, as an image of the whole slider.

        (Of the whole slider: the macOS style mirrors inverted sliders around the
        slider's rect, and ignores clipping.) `ratio` is the image's pixel ratio.
        """
        image = QImage(self.size() * ratio, QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(ratio)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        (style or self.style()).drawComplexControl(CC_SLIDER, opt, painter, self)
        painter.end()
        return image

    def _fillBrush(self, opt: QStyleOptionSlider) -> QBrush:
        """The color that the style fills slider grooves with (else the palette's).

        (The palette's accent, grayed if disabled or if it's the window's color.)

        It's read from a groove that the style draws without tick marks (with them,
        macOS doesn't fill it), filled up to its maximum. (Not the style sheet's style,
        which may not fill it: the app's, unless the slider has its own.)
        """
        style = self.style()
        if not self.testAttribute(Qt.WidgetAttribute.WA_SetStyle):
            style = QApplication.style()
        option = QStyleOptionSlider(opt)
        option.tickPosition = QSlider.TickPosition.NoTicks
        ratio = self.devicePixelRatioF()  # (any: it's only for its color)
        empty = self._grooveImage(option, option.minimum, ratio, style)
        full = self._grooveImage(option, option.maximum, ratio, style)
        center = _bounds(full).center() * ratio
        x, y = int(center.x()), int(center.y())
        if full.valid(x, y) and full.pixel(x, y) != empty.pixel(x, y):
            return QBrush(full.pixelColor(x, y))
        palette = opt.palette
        grayed = palette.brush(
            QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText
        )
        if palette.currentColorGroup() == QPalette.ColorGroup.Disabled:
            return grayed
        role = getattr(QPalette.ColorRole, "Accent", QPalette.ColorRole.Highlight)
        brush = palette.brush(role)  # (`Accent` is new in Qt 6.6)
        # (Qt's Windows palettes have it in the window's color in inactive windows)
        if brush.color() == palette.color(QPalette.ColorRole.Window):
            return grayed
        return brush

    def _barBrush(self, opt: QStyleOptionSlider) -> QBrush | None:
        """The custom color of the bar, in the slider's current state (if any)."""
        group = opt.palette.currentColorGroup()
        colors = self._style
        if group == QPalette.ColorGroup.Disabled:
            color = colors.brush_disabled
        elif group == QPalette.ColorGroup.Inactive:
            color = colors.brush_inactive or colors.brush_active
        else:
            color = colors.brush_active
        return _to_brush(color)

    def _draw_handle(self, painter: QStylePainter, opt: QStyleOptionSlider):
        opt.subControls = SC_HANDLE
        pidx = self._pressedIndex if self._pressedControl == SC_HANDLE else -1
        hidx = self._hoverIndex if self._hoverControl == SC_HANDLE else -1
        positions = self._optSliderPositions
        # (the handle at the left, or top)
        first = (max if opt.upsideDown else min)(
            range(len(positions)), key=positions.__getitem__
        )
        pages = self._pagesWithHandles(painter, opt)
        for idx, pos in enumerate(positions):
            opt.sliderPosition = pos
            # make pressed handles appear sunken
            if idx == pidx:
                opt.state |= QStyle.StateFlag.State_Sunken
            else:
                opt.state = opt.state & ~QStyle.StateFlag.State_Sunken
            opt.activeSubControls = SC_HANDLE if idx == hidx else SC_NONE
            self._drawHandle(painter, opt, pages, first=idx == first)

    def _pagesWithHandles(
        self, painter: QStylePainter, opt: QStyleOptionSlider
    ) -> tuple[bool, bool]:
        """Whether the style draws a page before each handle, and one after it.

        (Style sheets' sub-page and add-page, which Qt draws with each handle up to
        6.10.0: https://bugreports.qt.io/browse/QTBUG-141157.) With a handle at two
        places, off screen: a page runs from an end of the groove to the handle, so
        it grows or shrinks as the handle moves, while a handle, and its shadow or
        glow (however far it reaches), moves with it.
        """
        if not _PAGES_WITH_EACH_HANDLE:
            return False, False
        ratio = _ratio(painter)
        quarter = (opt.maximum - opt.minimum) // 4
        one = self._pastHandle(opt, opt.minimum + quarter, ratio)
        other = self._pastHandle(opt, opt.maximum - quarter, ratio)
        return abs(one[0] - other[0]) > 1, abs(one[1] - other[1]) > 1

    def _pastHandle(
        self, opt: QStyleOptionSlider, position: int, ratio: float
    ) -> tuple[float, float]:
        """How far what the style draws for a handle at `position` reaches past it.

        (Before it, and after it: at its left and right, or top and bottom.)
        """
        option = QStyleOptionSlider(opt)
        option.subControls = SC_HANDLE
        option.sliderPosition = position
        drawn = _bounds(self._sliderImage(option, ratio))
        if drawn.isEmpty():
            return 0.0, 0.0
        rect = QRectF(self.style().subControlRect(CC_SLIDER, option, SC_HANDLE, self))
        if opt.orientation == Qt.Orientation.Horizontal:
            return rect.left() - drawn.left(), drawn.right() - rect.right()
        return rect.top() - drawn.top(), drawn.bottom() - rect.bottom()

    def _drawHandle(
        self,
        painter: QStylePainter,
        opt: QStyleOptionSlider,
        pages: tuple[bool, bool] = (False, False),
        first: bool = False,
    ) -> None:
        """Draw a handle, without the style sheet's sub-page and add-page (`pages`).

        Up to 6.10.0, Qt draws them with each handle, over the bar: then only the
        handle's own rect is drawn (https://bugreports.qt.io/browse/QTBUG-141157).
        The pages show in it around a round handle, in the groove. With a page on one
        side, only what the handle's mirror image covers too is drawn there. With
        pages on both sides, they're kept on the right sides: the bar's (the
        sub-page's) is before each handle, at its left or top. So the `first` handle,
        at the left or top, with the bar on its other side, is drawn upside down,
        then mirrored back.
        """
        if any(pages):  # (style sheet handles, which don't blend with what's behind)
            ratio = _ratio(painter)
            rect = self.style().subControlRect(CC_SLIDER, opt, SC_HANDLE, self)
            if all(pages) and first:
                image = _crop(self._mirroredHandle(opt, rect, ratio), rect)
            else:
                image = _crop(self._sliderImage(opt, ratio), rect)
            if not all(pages):
                groove = self.style().subControlRect(CC_SLIDER, opt, SC_GROOVE, self)
                horizontal = opt.orientation == Qt.Orientation.Horizontal
                band = groove.translated(-rect.topLeft())
                image = _symmetric(image, band, horizontal)
            painter.drawImage(rect.topLeft(), image)
            return
        # (directly: native handles may blend with what's behind them, e.g. on macOS)
        painter.drawComplexControl(CC_SLIDER, opt)

    def _mirroredHandle(
        self, opt: QStyleOptionSlider, rect: QRect, ratio: float
    ) -> QImage:
        """The handle in `rect`, drawn upside down, then mirrored back onto `rect`."""
        option = QStyleOptionSlider(opt)
        option.upsideDown = not opt.upsideDown
        there = self.style().subControlRect(CC_SLIDER, option, SC_HANDLE, self)
        image = QImage(self.size() * ratio, QImage.Format.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(ratio)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        if opt.orientation == Qt.Orientation.Horizontal:
            painter.translate(rect.x() + there.x() + rect.width(), 0)
            painter.scale(-1, 1)
        else:
            painter.translate(0, rect.y() + there.y() + rect.height())
            painter.scale(1, -1)
        self.style().drawComplexControl(CC_SLIDER, option, painter, self)
        painter.end()
        return image

    def _updateHoverControl(self, pos):
        old_hover = self._hoverControl, self._hoverIndex
        self._hoverControl, self._hoverIndex = self._getControlAtPos(pos)
        if (self._hoverControl, self._hoverIndex) != old_hover:
            self.update()

    def _updatePressedControl(self, pos):
        opt = self._styleOption
        self._pressedControl, self._pressedIndex = self._getControlAtPos(pos, opt)

    def _setClickOffset(self, pos):
        if self._pressedControl == SC_BAR:
            self._clickOffset = self._pixelPosToRangeValue(self._pick(pos))
            self._sldPosAtPress = tuple(self._position)
        elif self._pressedControl == SC_HANDLE:
            hr = self._handleRect(self._pressedIndex)
            self._clickOffset = self._pick(pos - hr.topLeft())

    # NOTE: this is very much tied to mousepress... not a generic "get control"
    def _getControlAtPos(
        self, pos: QPoint, opt: QStyleOptionSlider | None = None
    ) -> tuple[QStyle.SubControl, int]:
        """Update self._pressedControl based on ev.pos()."""
        opt = opt or self._styleOption

        if isinstance(pos, QPointF):
            pos = pos.toPoint()

        for i in range(len(self._position)):
            if self._handleRect(i, opt).contains(pos):
                return (SC_HANDLE, i)

        click_pos = self._pixelPosToRangeValue(self._pick(pos))
        for i, p in enumerate(self._position):
            if p > click_pos:
                if i > 0:
                    # the click was in an internal segment
                    if self._bar_moves_all:
                        return (SC_BAR, i)
                    avg = (self._position[i - 1] + self._position[i]) / 2
                    return (SC_HANDLE, i - 1 if click_pos < avg else i)
                # the click was below the minimum slider
                return (SC_HANDLE, 0)
        # the click was above the maximum slider
        return (SC_HANDLE, len(self._position) - 1)

    def _execute_scroll(self, steps_to_scroll, modifiers):
        if modifiers & Qt.KeyboardModifier.AltModifier:
            self._spreadAllPositions(shrink=steps_to_scroll < 0)
        else:
            self._offsetAllPositions(steps_to_scroll)
        self.triggerAction(QSlider.SliderAction.SliderMove)

    def _has_scroll_space_left(self, offset):
        return (offset > 0 and max(self._value) < self._maximum) or (
            offset < 0 and min(self._value) < self._minimum
        )

    def _spreadAllPositions(self, shrink=False, gain=1.1, ref=None) -> None:
        if ref is None:
            ref = self._position
        # if self._bar_is_rigid:  # TODO

        if shrink:
            gain = 1 / gain
        center = abs(ref[-1] + ref[0]) / 2
        self.setSliderPosition([((i - center) * gain) + center for i in ref])


@dataclass
class _BarColors:
    """Custom colors of the bar, for each state (`None`: the style's own).

    `barColor` sets `brush_active`, which is also used for inactive windows. (It's the
    slider's `_style`, whose attributes some projects set directly.)
    """

    brush_active: Any = None
    brush_inactive: Any = None
    brush_disabled: Any = None


def _ratio(painter: QPainter) -> float:
    """The scale of what the painter paints on (e.g. 2 for a 2x image).

    (Not the widget's ratio: when rendered to an image, it's the screen's.)
    """
    transform = painter.deviceTransform()
    return max(abs(transform.m11()), abs(transform.m22())) or 1.0


def _apart(rect: QRect, other: QRect, horizontal: bool) -> QRect:
    """The part of `rect` that's not on `other`, on its side (along the slider)."""
    if not rect.intersects(other):
        return QRect(rect)
    out = QRect(rect)
    if horizontal and other.center().x() >= rect.center().x():
        out.setRight(other.left() - 1)
    elif horizontal:
        out.setLeft(other.right() + 1)
    elif other.center().y() >= rect.center().y():
        out.setBottom(other.top() - 1)
    else:
        out.setTop(other.bottom() + 1)
    return out


def _crop(image: QImage, rect: QRect) -> QImage:
    """The part of `image` in `rect` (in logical pixels)."""
    ratio = image.devicePixelRatio()
    pixels = QRectF(QPointF(rect.topLeft()) * ratio, QSizeF(rect.size()) * ratio)
    part = image.copy(pixels.toAlignedRect())
    part.setDevicePixelRatio(ratio)
    return part


def _symmetric(image: QImage, rect: QRect, horizontal: bool) -> QImage:
    """`image`, in `rect`, only where its mirror image (along the slider) is too."""
    out = QImage(image)
    painter = QPainter(out)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.setClipRect(rect)
    ratio = image.devicePixelRatio()
    if horizontal:
        painter.translate(image.width() / ratio, 0)
        painter.scale(-1, 1)
    else:
        painter.translate(0, image.height() / ratio)
        painter.scale(1, -1)
    painter.drawImage(0, 0, image)
    painter.end()
    return out


def _bounds(image: QImage) -> QRectF:
    """The bounds of the image's pixels that aren't transparent (in logical pixels).

    (Even faint ones: the macOS groove is a black overlay with an alpha of ~5%.)
    """
    alpha = image.convertToFormat(QImage.Format.Format_Alpha8)
    bits = alpha.constBits()
    if hasattr(bits, "setsize"):  # (PyQt)
        bits.setsize(alpha.sizeInBytes())
    data, stride, width = bytes(bits), alpha.bytesPerLine(), alpha.width()
    rows, left, right = [], width, -1
    for y in range(alpha.height()):
        row = data[y * stride : y * stride + width]
        if visible := row.lstrip(b"\0"):
            rows.append(y)
            left = min(left, width - len(visible))
            right = max(right, len(row.rstrip(b"\0")) - 1)
    if not rows:
        return QRectF()
    ratio = image.devicePixelRatio()
    pixels = QRectF(left, rows[0], right - left + 1, rows[-1] - rows[0] + 1)
    return QRectF(pixels.topLeft() / ratio, pixels.size() / ratio)


def _to_brush(color: Any) -> QBrush | None:
    """`color` as a brush: a QBrush, QColor, QGradient, or a string (see `_parse`)."""
    if color is None or isinstance(color, QBrush):
        return color
    if isinstance(color, str):
        color = _parse(color)
        return None if color is None else QBrush(color)
    return QBrush(color)  # (a QColor, QGradient, or Qt.GlobalColor)


_NUM = r"(\d*\.?\d+)"
_RGBA = re.compile(r"rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*(\d+)?\)")
_LINEAR = re.compile(
    rf"qlineargradient\(x1:\s*{_NUM},\s*y1:\s*{_NUM},\s*x2:\s*{_NUM},\s*"
    rf"y2:\s*{_NUM},\s*stop:0\s*(\S+),.*stop:1\s*(\S+)\)"
)
_RADIAL = re.compile(
    rf"qradialgradient\(cx:\s*{_NUM},\s*cy:\s*{_NUM},\s*radius:\s*{_NUM},\s*"
    rf"fx:\s*{_NUM},\s*fy:\s*{_NUM},\s*stop:0\s*(\S+),.*stop:1\s*(\S+)\)"
)


def _parse(color: str) -> QColor | QGradient | None:
    """A color name, `"#rrggbb"`, `"rgba(r, g, b, a)"`, or a QSS gradient."""
    if (qcolor := QColor(color)).isValid():
        return qcolor
    if match := _RGBA.search(color):
        return QColor(*(int(x) if x else 255 for x in match.groups()))
    gradient: QGradient
    if match := _LINEAR.search(color):
        *coords, stop0, stop1 = match.groups()
        gradient = QLinearGradient(*map(float, coords))
    elif match := _RADIAL.search(color):
        *coords, stop0, stop1 = match.groups()
        gradient = QRadialGradient(*map(float, coords))
    else:
        return None
    # (coordinates are relative to the bar, as in style sheets)
    gradient.setCoordinateMode(QGradient.CoordinateMode.ObjectBoundingMode)
    gradient.setColorAt(0, QColor(stop0))
    gradient.setColorAt(1, QColor(stop1))
    return gradient
