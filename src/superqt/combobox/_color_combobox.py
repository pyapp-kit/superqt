from __future__ import annotations

import warnings
from contextlib import suppress
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, Literal, cast

from qtpy.QtCore import QModelIndex, QPersistentModelIndex, QRect, QSize, Qt, Signal
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import (
    QAbstractItemDelegate,
    QColorDialog,
    QComboBox,
    QLineEdit,
    QStyle,
    QStyleOptionViewItem,
    QWidget,
)

from superqt.utils import signals_blocked

if TYPE_CHECKING:
    from collections.abc import Sequence

_NAME_MAP = {QColor(x).name(): x for x in QColor.colorNames()}

COLOR_ROLE = Qt.ItemDataRole.BackgroundRole


class InvalidColorPolicy(IntEnum):
    """Policy for handling invalid colors."""

    Ignore = auto()
    Warn = auto()
    Raise = auto()


class _ColorComboLineEdit(QLineEdit):
    """A read-only line edit that shows the parent ComboBox popup when clicked."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        # hide any original text
        self.setStyleSheet("color: transparent")
        self.setText("")

    def mouseReleaseEvent(self, _: Any) -> None:
        """Show parent popup when clicked.

        Without this, only the down arrow will show the popup.  And if mousePressEvent
        is used instead, the popup will show and then immediately hide.
        """
        parent = self.parent()
        if hasattr(parent, "showPopup"):
            parent.showPopup()


class _ColorComboItemDelegate(QAbstractItemDelegate):
    """Delegate that draws color squares in the ComboBox.

    This provides more control than simply setting various data roles on the item,
    and makes for a nicer appearance. Importantly, it prevents the color from being
    obscured on hover.
    """

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        return QSize(20, 20)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        color: QColor | None = index.data(COLOR_ROLE)
        rect = cast("QRect", option.rect)  # type: ignore
        state = cast("QStyle.StateFlag", option.state)  # type: ignore
        selected = state & QStyle.StateFlag.State_Selected
        border = QColor("lightgray")

        if not color:
            # not a color square, just draw the text
            text_color = Qt.GlobalColor.black if selected else Qt.GlobalColor.gray
            painter.setPen(text_color)
            text = index.data(Qt.ItemDataRole.DisplayRole)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            return

        # slightly larger border for rect
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor(border)
        painter.setPen(pen)

        if selected:
            # if hovering, give a slight highlight and draw the color name
            painter.setBrush(color.lighter(110))
            painter.drawRect(rect)
            # use user friendly color name if available
            name = _NAME_MAP.get(color.name(), color.name())
            painter.setPen(_pick_font_color(color))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, name)
        else:  # not hovering
            painter.setBrush(color)
            painter.drawRect(rect)


class QColorComboBox(QComboBox):
    """A drop down menu for selecting colors.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget.
    allow_user_colors : bool, optional
        Whether to show an "Add Color" item that opens a QColorDialog when clicked.
        Whether the user can add custom colors by clicking the "Add Color" item.
        Default is False. Can also be set with `setUserColorsAllowed`.
    add_color_text: str, optional
        The text to display for the "Add Color" item. Default is "Add Color...".
    """

    currentColorChanged = Signal(QColor)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        allow_user_colors: bool = False,
        add_color_text: str = "Add Color...",
    ) -> None:
        # init QComboBox
        super().__init__(parent)
        self._invalid_policy: InvalidColorPolicy = InvalidColorPolicy.Ignore
        self._add_color_text: str = add_color_text
        self._allow_user_colors: bool = allow_user_colors
        self._last_color: QColor = QColor()

        self.setLineEdit(_ColorComboLineEdit(self))
        self.setItemDelegate(_ColorComboItemDelegate())

        self.currentIndexChanged.connect(self._on_index_changed)
        self.activated.connect(self._on_activated)

        self.setUserColorsAllowed(allow_user_colors)

    def setInvalidColorPolicy(
        self, policy: InvalidColorPolicy | int | Literal["Raise", "Ignore", "Warn"]
    ) -> None:
        """Sets the policy for handling invalid colors."""
        if isinstance(policy, str):
            policy = InvalidColorPolicy[policy]
        elif isinstance(policy, int):
            policy = InvalidColorPolicy(policy)
        elif not isinstance(policy, InvalidColorPolicy):
            raise TypeError(f"Invalid policy type: {type(policy)!r}")
        self._invalid_policy = policy

    def invalidColorPolicy(self) -> InvalidColorPolicy:
        """Returns the policy for handling invalid colors."""
        return self._invalid_policy

    InvalidColorPolicy = InvalidColorPolicy

    def userColorsAllowed(self) -> bool:
        """Returns whether the user can add custom colors."""
        return self._allow_user_colors

    def setUserColorsAllowed(self, allow: bool) -> None:
        """Sets whether the user can add custom colors."""
        self._allow_user_colors = bool(allow)

        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx < 0:
            if self._allow_user_colors:
                self.addItem(self._add_color_text)
        elif not self._allow_user_colors:
            self.removeItem(idx)

    def clear(self) -> None:
        """Clears the QComboBox of all entries (leaves "Add colors" if enabled)."""
        super().clear()
        self.setUserColorsAllowed(self._allow_user_colors)

    def addColor(self, color: Any) -> None:
        """Adds the color to the QComboBox."""
        _color = _cast_color(color)
        if not _color.isValid():
            if self._invalid_policy == InvalidColorPolicy.Raise:
                raise ValueError(f"Invalid color: {color!r}")
            elif self._invalid_policy == InvalidColorPolicy.Warn:
                warnings.warn(f"Ignoring invalid color: {color!r}", stacklevel=2)
            return

        c = self.currentColor()
        if self.findData(_color) > -1:  # avoid duplicates
            return

        # add the new color and set the background color of that item
        self.addItem("", _color)
        self.setItemData(self.count() - 1, _color, COLOR_ROLE)
        if not c or not c.isValid():
            self._on_index_changed(self.count() - 1)

        # make sure the "Add Color" item is last
        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx >= 0:
            with signals_blocked(self):
                self.removeItem(idx)
                self.addItem(self._add_color_text)

    def itemColor(self, index: int) -> QColor | None:
        """Returns the color of the item at the given index."""
        return self.itemData(index, COLOR_ROLE)

    def addColors(self, colors: Sequence[Any]) -> None:
        """Adds colors to the QComboBox."""
        for color in colors:
            self.addColor(color)

    def currentColor(self) -> QColor | None:
        """Returns the currently selected QColor or None if not yet selected."""
        return self.currentData(COLOR_ROLE)

    def setCurrentColor(self, color: Any) -> None:
        """Adds the color to the QComboBox and selects it."""
        idx = self.findData(_cast_color(color), COLOR_ROLE)
        if idx >= 0:
            self.setCurrentIndex(idx)

    def currentColorName(self) -> str | None:
        """Returns the name of the currently selected QColor or black if None."""
        color = self.currentColor()
        return color.name() if color else "#000000"

    def _on_activated(self, index: int) -> None:
        if self.itemText(index) != self._add_color_text:
            return

        # show temporary text while dialog is open
        self.lineEdit().setStyleSheet("background-color: white; color: gray;")
        self.lineEdit().setText("Pick a Color ...")
        try:
            color = QColorDialog.getColor()
        finally:
            self.lineEdit().setText("")

        if color.isValid():
            # add the color and select it
            self.addColor(color)
        elif self._last_color.isValid():
            # user canceled, restore previous color without emitting signal
            idx = self.findData(self._last_color, COLOR_ROLE)
            if idx >= 0:
                with signals_blocked(self):
                    self.setCurrentIndex(idx)
                hex_ = self._last_color.name()
                self.lineEdit().setStyleSheet(f"background-color: {hex_};")
            return

    def _on_index_changed(self, index: int) -> None:
        color = self.itemData(index, COLOR_ROLE)
        if isinstance(color, QColor):
            self.lineEdit().setStyleSheet(f"background-color: {color.name()};")
            self.currentColorChanged.emit(color)
            self._last_color = color


def _cast_color(val: Any) -> QColor:
    with suppress(TypeError):
        color = QColor(val)
        if color.isValid():
            return color
    if isinstance(val, (tuple, list)):
        with suppress(TypeError):
            color = QColor(*val)
            if color.isValid():
                return color
    return QColor()


def _pick_font_color(color: QColor) -> QColor:
    """Pick a font shade that contrasts with the given color."""
    if (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114) > 80:
        return QColor(0, 0, 0, 128)
    else:
        return QColor(255, 255, 255, 128)
