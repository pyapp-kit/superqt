import warnings
from contextlib import suppress
from enum import IntEnum, auto
from typing import Any, Sequence, cast

from qtpy.QtCore import QModelIndex, QRect, QSize, Qt, Signal
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import (
    QColorDialog,
    QComboBox,
    QLineEdit,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from superqt.utils import signals_blocked

NAME_MAP = {QColor(x).name(): x for x in QColor.colorNames()}


class InvalidPolicy(IntEnum):
    """Policy for handling invalid colors."""

    Ignore = auto()
    Warn = auto()
    Raise = auto()


class _ComboLine(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def mouseReleaseEvent(self, arg__1) -> None:
        with suppress(AttributeError):
            self.parent().showPopup()


class _ComboDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index) -> QSize:
        return super().sizeHint(option, index).expandedTo(QSize(40, 20))

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        color: QColor | None = index.data(Qt.ItemDataRole.BackgroundRole)
        rect = cast("QRect", option.rect)  # type: ignore

        if not color:
            if option.state & QStyle.StateFlag.State_MouseOver:
                painter.setPen(Qt.GlobalColor.black)
            else:
                painter.setPen(Qt.GlobalColor.gray)
            text = index.data(Qt.ItemDataRole.DisplayRole)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
            return

        # slightly larger border for rect
        pen = painter.pen()
        pen.setWidth(2)
        pen.setColor("lightgray")
        painter.setPen(pen)
        if option.state & QStyle.StateFlag.State_MouseOver:  # hovering
            painter.setBrush(color.lighter(120))
            painter.drawRect(rect)

            # draw name on hover
            name = NAME_MAP.get(color.name(), color.name())
            painter.setPen(_pick_font_color(color))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, name)
        else:  # not hovering
            painter.setBrush(color)
            painter.drawRect(rect)

        # return super().paint(painter, option, index)


class QColorComboBox(QComboBox):
    """A drop down menu for selecting colors."""

    # Adapted from https://stackoverflow.com/questions/64497029/a-color-drop-down-selector-for-pyqt5

    # signal emitted if a color has been selected
    currentColorChanged = Signal(QColor)

    def __init__(
        self, parent: QWidget | None = None, allow_user_colors: bool = False
    ) -> None:
        # init QComboBox
        super().__init__(parent)
        self._invalid_policy: InvalidPolicy = InvalidPolicy.Ignore
        self._add_color_text: str = "Add Color"
        self._allow_user_colors: bool = allow_user_colors

        self.setLineEdit(_ComboLine(self))
        self.setItemDelegate(_ComboDelegate())
        self.setMinimumHeight(20)

        self.currentIndexChanged.connect(self._index_changed)
        self.activated.connect(self._activated)

        if allow_user_colors:
            self.addItem(self._add_color_text)
            self.lineEdit().setStyleSheet("color: transparent")

    def sizeHint(self) -> QSize:
        return super().sizeHint().expandedTo(QSize(70, 0))

    def setInvalidPolicy(self, policy: InvalidPolicy) -> None:
        """Sets the policy for handling invalid colors."""
        if isinstance(policy, str):
            policy = InvalidPolicy[policy]
        elif isinstance(policy, int):
            policy = InvalidPolicy(policy)
        elif not isinstance(policy, InvalidPolicy):
            raise TypeError(f"Invalid policy type: {type(policy)!r}")
        self._invalid_policy = policy

    def invalidPolicy(self) -> InvalidPolicy:
        """Returns the policy for handling invalid colors."""
        return self._invalid_policy

    def userColorsAllowed(self) -> bool:
        """Returns whether the user can add custom colors."""
        return self._allow_user_colors

    def setUserColorsAllowed(self, allow: bool) -> None:
        """Sets whether the user can add custom colors."""
        self._allow_user_colors = bool(allow)

    def addColor(self, color: Any) -> None:
        """Adds the color to the QComboBox."""
        _color = _cast_color(color)
        if not _color.isValid():
            if self._invalid_policy == InvalidPolicy.Raise:
                raise ValueError(f"Invalid color: {color!r}")
            elif self._invalid_policy == InvalidPolicy.Warn:
                warnings.warn(f"Ignoring invalid color: {color!r}", stacklevel=2)
            return

        c = self.currentColor()
        if self.findData(_color) > -1:  # avoid duplicates
            return

        add_custom = False
        if self.itemText(self.count() - 1) == self._add_color_text:
            self.removeItem(self.count() - 1)
            add_custom = True

        # add the new color and set the background color of that item
        self.addItem("", _color)
        self.setItemData(self.count() - 1, _color, Qt.ItemDataRole.BackgroundRole)
        if not c or not c.isValid():
            self._index_changed(self.count() - 1)

        if add_custom:
            with signals_blocked(self):
                self.addItem(self._add_color_text)

    def addColors(self, colors: Sequence[Any]) -> None:
        """Adds colors to the QComboBox."""
        for color in colors:
            self.addColor(color)

    def currentColor(self) -> QColor | None:
        """Returns the currently selected QColor or None if not yet selected."""
        return self.currentData(Qt.ItemDataRole.BackgroundRole)

    def setCurrentColor(self, color: Any) -> None:
        """Adds the color to the QComboBox and selects it."""
        idx = self.findData(_cast_color(color), Qt.ItemDataRole.BackgroundRole)
        print(idx)
        if idx >= 0:
            self.setCurrentIndex(idx)

    def currentColorName(self) -> str | None:
        """Returns the name of the currently selected QColor or black if None."""
        color = self.currentColor()
        return color.name() if color else "#000000"

    def _activated(self, index: int) -> None:
        # if the user wants to define a custom color
        if self.itemText(index) == self._add_color_text:
            # get the user defined color
            new_color = QColorDialog.getColor()
            if new_color.isValid():
                # add the color to the QComboBox and emit the signal
                with signals_blocked(self):
                    self.addColor(new_color)
                idx = self.findData(new_color, Qt.ItemDataRole.BackgroundRole)
                self.setCurrentIndex(idx)

    def _index_changed(self, index: int) -> None:
        # make sure that current color is displayed
        if color := self.itemData(index, Qt.ItemDataRole.BackgroundRole):
            self.lineEdit().setStyleSheet(
                f"background-color: {color.name()}; color: transparent"
            )
        if color := self.currentColor():
            self.currentColorChanged.emit(color)


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
    if (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114) > 80:
        return QColor(0, 0, 0, 128)
    else:
        return QColor(255, 255, 255, 128)


if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication([])
    w = QColorComboBox()
    w.addColors(["red", "blue", "green", "lime", "magenta"])
    w.setCurrentColor(QColor("magenta"))
    w.show()
    w.currentColorChanged.connect(lambda x: print(w.currentColorName()))
    app.exec_()
