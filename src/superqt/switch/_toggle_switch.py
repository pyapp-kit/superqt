from __future__ import annotations

from typing import overload

from qtpy import QtCore, QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Property, Qt


class QStyleOptionToggleSwitch(QtW.QStyleOptionButton):
    def __init__(self):
        super().__init__()
        self.on_color = QtGui.QColor("#4D79C7")
        self.off_color = QtGui.QColor("#909090")
        self.handle_color = QtGui.QColor("#d5d5d5")
        self.switch_width = 24
        self.switch_height = 12
        self.handle_size = 14

        # these aren't yet overrideable in QToggleSwitch
        self.margin = 2
        self.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class QToggleSwitch(QtW.QAbstractButton):
    StyleOption = QStyleOptionToggleSwitch

    @overload
    def __init__(self, parent: QtW.QWidget | None = ...) -> None: ...
    @overload
    def __init__(self, text: str | None, parent: QtW.QWidget | None = ...) -> None: ...

    def __init__(  # type: ignore [misc]  # overload
        self, text: str | None = None, parent: QtW.QWidget | None = None
    ) -> None:
        if isinstance(text, QtW.QWidget):
            if parent is not None:
                raise TypeError("No overload of QToggleSwitch matches the arguments")
            parent = text
            text = None

        # attributes for drawing the switch
        self._on_color = QtGui.QColor("#4D79C7")
        self._off_color = QtGui.QColor("#909090")
        self._handle_color = QtGui.QColor("#d5d5d5")
        self._switch_width = 24
        self._switch_height = 12
        self._handle_size = 14
        self._offset_value = 8.0

        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggled.connect(self._animate_handle)

        self._anim = QtCore.QPropertyAnimation(self, b"_offset", self)
        self._anim.setDuration(120)
        self._offset_value = self._offset_for_checkstate(False)
        if text:
            self.setText(text)

    def initStyleOption(self, option: QStyleOptionToggleSwitch) -> None:
        """Initialize the style option for the switch."""
        option.initFrom(self)

        option.text = self.text()
        option.icon = self.icon()
        option.iconSize = self.iconSize()
        option.state |= (
            QtW.QStyle.StateFlag.State_On
            if self.isChecked()
            else QtW.QStyle.StateFlag.State_Off
        )

        option.on_color = self.onColor
        option.off_color = self.offColor
        option.handle_color = self.handleColor
        option.switch_width = self.switchWidth
        option.switch_height = self.switchHeight
        option.handle_size = self.handleSize

    def paintEvent(self, a0: QtGui.QPaintEvent | None) -> None:
        p = QtGui.QPainter(self)
        opt = QStyleOptionToggleSwitch()
        self.initStyleOption(opt)
        self.drawGroove(p, self._groove_rect(opt), opt)
        p.save()
        self.drawHandle(p, self._handle_rect(opt), opt)
        p.restore()
        self.drawText(p, self._text_rect(opt), opt)
        p.end()

    def minimumSizeHint(self) -> QtCore.QSize:
        return self.sizeHint()

    def setAnimationDuration(self, msec: int) -> None:
        """Set the duration of the animation in milliseconds.

        To disable animation, set duration to 0.
        """
        self._anim.setDuration(msec)

    def animationDuration(self) -> int:
        """Return the duration of the animation in milliseconds."""
        return self._anim.duration()

    def sizeHint(self) -> QtCore.QSize:
        self.ensurePolished()
        opt = QStyleOptionToggleSwitch()
        self.initStyleOption(opt)

        fm = QtGui.QFontMetrics(self.font())
        text_size = fm.size(0, self.text())
        height = max(opt.switch_height, text_size.height()) + opt.margin * 2
        width = opt.switch_width + text_size.width() + opt.margin * 2 + 8
        return QtCore.QSize(width, height)

    ### Re-implementable methods for drawing the switch ###

    def drawGroove(
        self,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        option: QStyleOptionToggleSwitch,
    ) -> None:
        """Draw the groove of the switch.

        Parameters
        ----------
        painter : QtGui.QPainter
            The painter to use for drawing.
        rect : QtCore.QRectF
            The rectangle in which to draw the groove.
        option : QStyleOptionToggleSwitch
            The style options used for drawing.
        """
        painter.setPen(Qt.PenStyle.NoPen)

        is_checked = option.state & QtW.QStyle.StateFlag.State_On
        is_enabled = option.state & QtW.QStyle.StateFlag.State_Enabled
        # draw the groove
        if is_enabled:
            painter.setBrush(option.on_color if is_checked else option.off_color)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            painter.setOpacity(0.8)
        else:
            painter.setBrush(option.off_color)
            painter.setOpacity(0.6)

        half_height = option.switch_height / 2
        painter.drawRoundedRect(rect, half_height, half_height)

    def drawHandle(
        self,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        option: QStyleOptionToggleSwitch,
    ) -> None:
        """Draw the handle of the switch.

        Parameters
        ----------
        painter : QtGui.QPainter
            The painter to use for drawing.
        rect : QtCore.QRectF
            The rectangle in which to draw the handle.
        option : QStyleOptionToggleSwitch
            The style options used for drawing.
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(option.handle_color)
        painter.setOpacity(1.0)
        painter.drawEllipse(rect)

    def drawText(
        self,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        option: QStyleOptionToggleSwitch,
    ) -> None:
        """Draw the text next to the switch.

        Parameters
        ----------
        painter : QtGui.QPainter
            The painter to use for drawing.
        rect : QtCore.QRectF
            The rectangle in which to draw the text.
        option : QStyleOptionToggleSwitch
            The style options used for drawing.
        """
        # TODO:
        # using self.style().drawControl(CE_PushButtonLabel ...)
        # might provide a more native experience.
        text_color = option.palette.color(self.foregroundRole())
        pen = QtGui.QPen(text_color, 1)
        painter.setPen(pen)
        painter.drawText(rect, int(option.text_alignment), option.text)

    ### Properties ###

    def _get_onColor(self) -> QtGui.QColor:
        return self._on_color

    def _set_onColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._on_color = QtGui.QColor(color)
        self.update()

    onColor = Property(QtGui.QColor, _get_onColor, _set_onColor)
    """Color of the switch groove when it is on."""

    def _get_offColor(self) -> QtGui.QColor:
        return self._off_color

    def _set_offColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._off_color = QtGui.QColor(color)
        self.update()

    offColor = Property(QtGui.QColor, _get_offColor, _set_offColor)
    """Color of the switch groove when it is off."""

    def _get_handleColor(self) -> QtGui.QColor:
        return self._handle_color

    def _set_handleColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._handle_color = QtGui.QColor(color)
        self.update()

    handleColor = Property(QtGui.QColor, _get_handleColor, _set_handleColor)
    """Color of the switch handle."""

    def _get_switchWidth(self) -> int:
        return self._switch_width

    def _set_switchWidth(self, width: int) -> None:
        self._switch_width = width
        self._offset_value = self._offset_for_checkstate(self.isChecked())
        self.update()

    switchWidth = Property(int, _get_switchWidth, _set_switchWidth)
    """Width of the switch groove."""

    def _get_switchHeight(self) -> int:
        return self._switch_height

    def _set_switchHeight(self, height: int) -> None:
        self._switch_height = height
        self._offset_value = self._offset_for_checkstate(self.isChecked())
        self.update()

    switchHeight = Property(int, _get_switchHeight, _set_switchHeight)
    """Height of the switch groove."""

    def _get_handleSize(self) -> int:
        return self._handle_size

    def _set_handleSize(self, size: int) -> None:
        self._handle_size = size
        self.update()

    handleSize = Property(int, _get_handleSize, _set_handleSize)
    """Width/height of the switch handle."""

    ### Other private methods ###

    def _animate_handle(self, val: bool) -> None:
        end = self._offset_for_checkstate(val)
        if self._anim.duration():
            self._anim.setStartValue(self._offset_for_checkstate(not val))
            self._anim.setEndValue(end)
            self._anim.start()
        else:
            self._set_offset(end)

    def _get_offset(self) -> float:
        return self._offset_value

    def _set_offset(self, offset: float) -> None:
        self._offset_value = offset
        self.update()

    _offset = Property(float, _get_offset, _set_offset)

    def _offset_for_checkstate(self, val: bool) -> float:
        opt = QStyleOptionToggleSwitch()
        self.initStyleOption(opt)
        if val:
            offset = opt.margin + opt.switch_width - opt.switch_height / 2
        else:
            offset = opt.margin + opt.switch_height / 2
        return offset

    def _groove_rect(self, opt: QStyleOptionToggleSwitch) -> QtCore.QRectF:
        return QtCore.QRectF(
            opt.margin, self._vertical_offset(opt), opt.switch_width, opt.switch_height
        )

    def _handle_rect(self, opt: QStyleOptionToggleSwitch) -> QtCore.QRectF:
        return QtCore.QRectF(
            self._offset_value - opt.handle_size / 2,
            self._vertical_offset(opt) - (opt.handle_size - opt.switch_height) / 2,
            opt.handle_size,
            opt.handle_size,
        )

    def _text_rect(self, opt: QStyleOptionToggleSwitch) -> QtCore.QRectF:
        # If handle is bigger than groove, adjust the text to the right of the handle.
        # If groove is bigger, adjust the text to the right of the groove.
        return QtCore.QRectF(
            opt.switch_width
            + max(opt.handle_size - opt.switch_height, 0) // 2
            + opt.margin * 2
            + 2,
            0,
            self.width() - opt.switch_width - opt.margin * 2,
            self.height(),
        )

    def _vertical_offset(self, opt: QStyleOptionToggleSwitch) -> int:
        """Offset for the vertical centering of the switch."""
        return (self.height() - opt.switch_height) // 2 + opt.margin
