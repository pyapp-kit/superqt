from __future__ import annotations

from typing import overload

from qtpy import QtCore, QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Property, Qt, Signal


class _QToggleSwitch(QtW.QWidget):
    toggled = Signal(bool)

    def __init__(self, parent: QtW.QWidget | None = None):
        super().__init__(parent)
        self.setSizePolicy(
            QtW.QSizePolicy.Policy.Minimum, QtW.QSizePolicy.Policy.Expanding
        )
        self._on_color = QtGui.QColor("#4D79C7")
        self._off_color = QtGui.QColor("#909090")
        self._handle_color = QtGui.QColor("#d5d5d5")
        self._margin = 2
        self._offset_value = 6
        self._checked = False
        self.setSize(12)
        self.toggled.connect(self._set_checked)
        self._anim = QtCore.QPropertyAnimation(self, b"_offset", self)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def size(self) -> int:
        """Size of the toggle switch."""
        return self._size

    def setSize(self, size: int):
        """Set the size of the toggle switch."""
        size = int(size)
        self._size = size
        self._offset = size // 2
        self.setFixedSize(
            (self._size + self._margin) * 2, self._size + self._margin * 2
        )

    def _get_offset(self) -> float:
        return self._offset_value

    def _set_offset(self, offset: float) -> None:
        self._offset_value = offset
        self.update()

    _offset = Property(float, _get_offset, _set_offset)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(2 * (self._size + self._margin), self.minimumHeight())

    def minimumHeight(self) -> int:
        return self._size + 2 * self._margin

    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setPen(Qt.PenStyle.NoPen)
        radius = self._size / 2
        rrect = QtCore.QRect(
            self._margin,
            self._margin,
            self.width() - 2 * self._margin,
            self.height() - 2 * self._margin,
        )
        if self.isEnabled():
            p.setBrush(self._on_color if self._checked else self._off_color)
            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
            p.setOpacity(0.8)
        else:
            p.setBrush(self._off_color)
            p.setOpacity(0.6)
        p.drawRoundedRect(rrect, radius, radius)
        p.setBrush(self._handle_color)
        p.setOpacity(1.0)
        p.drawEllipse(
            QtCore.QRectF(self._offset - radius, 0, self.height(), self.height())
        )

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent):
        if e.button() & Qt.MouseButton.LeftButton:
            self.toggled.emit(not self.isChecked())
        return super().mouseReleaseEvent(e)

    def toggle(self):
        return self.setChecked(not self.isChecked())

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, val: bool):
        self._set_checked(val)
        self.toggled.emit(val)

    def _set_checked(self, val: bool):
        # Do not re-animate if the value is the same
        if self._checked == val:
            return
        start = self._position_for_value(self._checked)
        end = self._position_for_value(val)

        self._checked = val
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.setDuration(120)
        self._anim.start()

    def _position_for_value(self, val: bool) -> int:
        if val:
            return int(self.width() - self.height() / 2 - self._margin)
        else:
            return self.height() // 2


class _QToggleSwitchLabel(QtW.QLabel):
    clicked = Signal()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() & Qt.MouseButton.LeftButton:
            self.clicked.emit()
        return None


class QToggleSwitch(QtW.QCheckBox):
    @overload
    def __init__(self, parent: QtW.QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QtW.QWidget | None = None) -> None: ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QtW.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._text_label = _QToggleSwitchLabel(super().text(), self)
        super().setText("")
        self._switch = _QToggleSwitch(self)
        self._text_label.clicked.connect(self._switch.toggle)
        layout.addWidget(self._switch)
        layout.addWidget(self._text_label)
        self.setMaximumHeight(self._switch.height())
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @property
    def toggled(self):
        return self.toggleSwitch().toggled

    def paintEvent(self, e):
        return QtW.QWidget.paintEvent(self, e)

    def toggleSwitch(self) -> _QToggleSwitch:
        """Return the toggle switch widget."""
        return self._switch

    def size(self) -> int:
        """Size of the switch."""
        return self.toggleSwitch().size()

    def setSize(self, size: int) -> None:
        """Set the size of the switch."""
        self.toggleSwitch().setSize(size)
        self.setMaximumHeight(self.toggleSwitch().height())

    def isChecked(self) -> bool:
        """Return True if the switch is checked."""
        return self.toggleSwitch().isChecked()

    def setChecked(self, val: bool) -> None:
        """Set the checked state of the switch."""
        self.toggleSwitch().setChecked(val)

    def text(self) -> str:
        """Text on the right side of the switch."""
        return self._text_label.text()

    def setText(self, text: str) -> None:
        """Set the text on the right side of the switch."""
        self._text_label.setText(text)

    def toggle(self) -> None:
        """Toggle the check state of the switch."""
        self.setChecked(not self.isChecked())

    def minimumHeight(self) -> int:
        return self.toggleSwitch().minimumHeight()

    def sizeHint(self) -> QtCore.QSize:
        switch_hint = self.toggleSwitch().sizeHint()
        text_hint = self._text_label.sizeHint()
        return QtCore.QSize(
            switch_hint.width() + text_hint.width(),
            max(switch_hint.height(), text_hint.height()),
        )

    def _get_onColor(self) -> QtGui.QColor:
        return self._switch._on_color

    def _set_onColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._switch._on_color = QtGui.QColor(color)
        self._switch.update()

    onColor = Property(QtGui.QColor, _get_onColor, _set_onColor)

    def _get_offColor(self) -> QtGui.QColor:
        return self._switch._off_color

    def _set_offColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._switch._off_color = QtGui.QColor(color)
        self._switch.update()

    offColor = Property(QtGui.QColor, _get_offColor, _set_offColor)

    def _get_handleColor(self) -> QtGui.QColor:
        return self._switch._handle_color

    def _set_handleColor(self, color: QtGui.QColor | QtGui.QBrush) -> None:
        self._switch._handle_color = QtGui.QColor(color)
        self._switch.update()

    handleColor = Property(QtGui.QColor, _get_handleColor, _set_handleColor)
