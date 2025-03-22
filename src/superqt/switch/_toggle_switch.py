from __future__ import annotations

from typing import overload

from qtpy import QtCore, QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Property, Qt


class QStyleOptionToggleSwitch(QtW.QStyleOptionButton):
    def __init__(self):
        super().__init__()
        self.margin = 2
        self.on_color = QtGui.QColor("#4D79C7")
        self.off_color = QtGui.QColor("#909090")
        self.handle_color = QtGui.QColor("#d5d5d5")
        self.switch_width = 24
        self.switch_height = 12
        self.handle_size = 14
        self.text_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class QToggleSwitch(QtW.QAbstractButton):
    StyleOption = QStyleOptionToggleSwitch

    @overload
    def __init__(self, parent: QtW.QWidget | None = ...) -> None: ...
    @overload
    def __init__(self, text: str | None, parent: QtW.QWidget | None = ...) -> None: ...

    def __init__(self, text=None, parent=None):
        if isinstance(text, QtW.QWidget):
            if parent is not None:
                raise TypeError("No overload of QToggleSwitch matches the arguments")
            parent = text
            text = None
        super().__init__(parent)
        self._style_option = self.StyleOption()  # the default style option
        self._style_option.text = text
        self._checked = False
        self._offset_value = self._offset_for_checkstate(self._checked)
        self._anim = QtCore.QPropertyAnimation(self, b"_offset", self)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def initStyleOption(self, option: QStyleOptionToggleSwitch) -> None:
        """Initialize the style option for the switch."""
        option.initFrom(self)
        option.text = self.text()
        option.on_color = self.onColor
        option.off_color = self.offColor
        option.handle_color = self.handleColor
        option.switch_width = self._style_option.switch_width
        option.switch_height = self._style_option.switch_height
        option.handle_size = self._style_option.handle_size
        option.margin = self._style_option.margin
        option.text_alignment = self._style_option.text_alignment
        return None

    def paintEvent(self, a0: QtGui.QPaintEvent | None) -> None:
        p = QtGui.QPainter(self)
        opt = QStyleOptionToggleSwitch()
        self.initStyleOption(opt)

        groove_rect = self._prep_draw_groove(p, opt)
        self.drawGroove(p, groove_rect, opt)
        handle_rect = self._prep_draw_handle(p, opt)
        self.drawHandle(p, handle_rect, opt)

        # paint text next to the switch
        text_rect = QtCore.QRect(
            opt.switch_width
            + (opt.handle_size - opt.switch_height) // 2
            + opt.margin * 2
            + 2,
            0,
            self.width() - opt.switch_width - opt.margin * 2,
            self.height(),
        )
        text_color = self.palette().color(self.foregroundRole())
        pen = QtGui.QPen(text_color, 1)
        p.setPen(pen)
        p.setFont(self.font())
        p.drawText(text_rect, opt.text_alignment, self.text())
        return None

    def minimumSizeHint(self) -> QtCore.QSize:
        return self.sizeHint()

    def sizeHint(self) -> QtCore.QSize:
        self.ensurePolished()
        opt = self.StyleOption()
        self.initStyleOption(opt)

        fm = QtGui.QFontMetrics(self.font())
        text_size = fm.size(0, self.text())
        height = max(opt.switch_height, text_size.height()) + opt.margin * 2
        width = opt.switch_width + text_size.width() + opt.margin * 2
        return QtCore.QSize(width, height)

    def mousePressEvent(self, e):
        if e.button() & Qt.MouseButton.LeftButton:
            self.pressed.emit()
        return None

    def mouseReleaseEvent(self, e):
        if e.button() & Qt.MouseButton.LeftButton and self.rect().contains(e.pos()):
            self.toggle()
            self.released.emit()
            self.clicked.emit()
        return None

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool) -> None:
        if self._checked == checked:
            return
        self._set_checked_animated(checked)
        self.toggled.emit(checked)

    def toggle(self) -> None:
        self.setChecked(not self.isChecked())
        return None

    def click(self) -> None:
        self.pressed.emit()
        self.toggle()
        self.released.emit()
        self.clicked.emit()
        return None

    def text(self) -> str:
        """Text displayed next to the switch."""
        return self._style_option.text or ""

    def setText(self, text: str | None) -> None:
        """Set the text displayed next to the switch."""
        self._style_option.text = text
        self.update()
        return None

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
            The style options (QToggleSwitch.StyleOption) used for drawing.
        """
        painter.drawRoundedRect(
            rect,
            option.switch_height / 2,
            option.switch_height / 2,
        )
        return None

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
            The rectangle in which to draw the groove.
        option : QStyleOptionToggleSwitch
            The style options (QToggleSwitch.StyleOption) used for drawing.
        """
        painter.drawEllipse(rect)
        return None

    ### Colors ###

    def _get_onColor(self) -> QtGui.QColor:
        return self._style_option.on_color

    def _set_onColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._style_option.on_color = QtGui.QColor(color)
        self.update()
        return None

    onColor = Property(QtGui.QColor, _get_onColor, _set_onColor)

    def _get_offColor(self) -> QtGui.QColor:
        return self._style_option.off_color

    def _set_offColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._style_option.off_color = QtGui.QColor(color)
        self.update()
        return None

    offColor = Property(QtGui.QColor, _get_offColor, _set_offColor)

    def _get_handleColor(self) -> QtGui.QColor:
        return self._style_option.handle_color

    def _set_handleColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._style_option.handle_color = QtGui.QColor(color)
        self.update()
        return None

    handleColor = Property(QtGui.QColor, _get_handleColor, _set_handleColor)

    ### Other private methods ###

    def _set_checked_animated(self, val: bool):
        start = self._offset_for_checkstate(self._checked)
        end = self._offset_for_checkstate(val)

        self._checked = val
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.setDuration(120)
        self._anim.start()
        return None

    def _get_offset(self) -> float:
        return self._offset_value

    def _set_offset(self, offset: float) -> None:
        self._offset_value = offset
        self.update()
        return None

    _offset = Property(float, _get_offset, _set_offset)

    def _offset_for_checkstate(self, val: bool) -> int:
        opt = self._style_option
        if val:
            offset = opt.margin + opt.switch_width - opt.switch_height / 2
        else:
            offset = opt.margin + opt.switch_height / 2
        return offset

    def _prep_draw_groove(
        self, p: QtGui.QPainter, opt: QStyleOptionToggleSwitch
    ) -> QtCore.QRect:
        p.setPen(Qt.PenStyle.NoPen)

        # draw the groove
        if self.isEnabled():
            p.setBrush(opt.on_color if self.isChecked() else opt.off_color)
            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            p.setOpacity(0.8)
        else:
            p.setBrush(opt.off_color)
            p.setOpacity(0.6)
        return QtCore.QRect(
            opt.margin,
            self._vertical_offset(opt),
            opt.switch_width,
            opt.switch_height,
        )

    def _prep_draw_handle(
        self, p: QtGui.QPainter, opt: QStyleOptionToggleSwitch
    ) -> QtCore.QRectF:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(opt.handle_color)
        p.setOpacity(1.0)
        return QtCore.QRectF(
            self._offset_value - opt.handle_size / 2,
            self._vertical_offset(opt) - (opt.handle_size - opt.switch_height) / 2,
            opt.handle_size,
            opt.handle_size,
        )

    def _vertical_offset(self, opt: QStyleOptionToggleSwitch) -> int:
        """Offset for the vertical centering of the switch."""
        return (self.height() - opt.switch_height) // 2 + opt.margin
