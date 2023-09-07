from __future__ import annotations

import warnings
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, Sequence, cast

from cmap import Colormap
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from superqt.utils import signals_blocked

from ._catalog_combo import CmapCatalogComboBox
from ._cmap_item_delegate import QColormapItemDelegate
from ._cmap_line_edit import QColormapLineEdit
from ._cmap_utils import try_cast_colormap

if TYPE_CHECKING:
    from cmap._colormap import ColorStopsLike


CMAP_ROLE = Qt.ItemDataRole.UserRole + 1


class InvalidPolicy(IntEnum):
    """Policy for handling invalid colors."""

    Ignore = auto()
    Warn = auto()
    Raise = auto()


class QColormapComboBox(QComboBox):
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
        The text to display for the "Add Color" item. Default is "Add Color".
    """

    currentColorChanged = Signal(QColor)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        allow_user_colors: bool = False,
        add_color_text: str = "Add Color",
    ) -> None:
        # init QComboBox
        super().__init__(parent)
        self._invalid_policy: InvalidPolicy = InvalidPolicy.Warn
        self._add_color_text: str = add_color_text
        self._allow_user_colors: bool = allow_user_colors
        self._last_cmap: Colormap | None = None

        self.setLineEdit(QColormapLineEdit(self))
        self.setItemDelegate(QColormapItemDelegate())

        self.currentIndexChanged.connect(self._on_index_changed)
        self.activated.connect(self._on_activated)

        self.setUserColorsAllowed(allow_user_colors)

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

        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx < 0:
            if self._allow_user_colors:
                self.addItem(self._add_color_text)
        elif not self._allow_user_colors:
            self.removeItem(idx)

    def clear(self) -> None:
        super().clear()
        self.setUserColorsAllowed(self._allow_user_colors)

    def addColormap(self, cmap: ColorStopsLike) -> None:
        """Adds the colormap to the QComboBox."""
        if (_cmap := try_cast_colormap(cmap)) is None:
            if self._invalid_policy == InvalidPolicy.Raise:
                raise ValueError(f"Invalid colormap: {cmap!r}")
            elif self._invalid_policy == InvalidPolicy.Warn:
                warnings.warn(f"Ignoring invalid colormap: {cmap!r}", stacklevel=2)
            return

        if self.findData(_cmap) > -1:  # avoid duplicates
            return

        c = self.currentColormap()
        # add the new color and set the background color of that item
        self.addItem(_cmap.name.rsplit(":", 1)[-1], _cmap)
        self.setItemData(self.count() - 1, _cmap, CMAP_ROLE)
        if not c:
            self._on_index_changed(self.count() - 1)

        # make sure the "Add Color" item is last
        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx >= 0:
            with signals_blocked(self):
                self.removeItem(idx)
                self.addItem(self._add_color_text)

    def itemColormap(self, index: int) -> QColor | None:
        """Returns the color of the item at the given index."""
        return self.itemData(index, CMAP_ROLE)

    def addColormaps(self, colors: Sequence[Any]) -> None:
        """Adds colors to the QComboBox."""
        for color in colors:
            self.addColormap(color)

    def currentColormap(self) -> QColor | None:
        """Returns the currently selected QColor or None if not yet selected."""
        return self.currentData(CMAP_ROLE)

    def setCurrentColormap(self, color: Any) -> None:
        """Adds the color to the QComboBox and selects it."""
        idx = self.findData(try_cast_colormap(color), CMAP_ROLE)
        if idx >= 0:
            self.setCurrentIndex(idx)

    def currentColormapName(self) -> str | None:
        """Returns the name of the currently selected QColor or black if None."""
        color = self.currentColormap()
        return color.name() if color else "#000000"

    def _on_activated(self, index: int) -> None:
        if self.itemText(index) != self._add_color_text:
            return

        # show temporary text while dialog is open
        # self.lineEdit().setStyleSheet("background-color: white; color: gray;")
        # self.lineEdit().setText("Pick a Color ...")
        try:
            dlg = _CmapNameDialog()
            dlg.exec()
        finally:
            pass
            # self.lineEdit().setText("")

        if cmap := dlg.colormap():
            # add the color and select it
            self.addColormap(cmap)
        elif self._last_cmap is not None:
            # user canceled, restore previous color without emitting signal
            idx = self.findData(self._last_cmap, CMAP_ROLE)
            if idx >= 0:
                with signals_blocked(self):
                    self.setCurrentIndex(idx)
                # hex_ = self._last_cmap.
                # self.lineEdit().setStyleSheet(f"background-color: {hex_};")
            return

    def _on_index_changed(self, index: int) -> None:
        colormap = self.itemData(index, CMAP_ROLE)
        if isinstance(colormap, Colormap):
            self.lineEdit().setColormap(colormap)
            self.currentColorChanged.emit(colormap)
            self._last_cmap = colormap

    def lineEdit(self) -> QColormapLineEdit:
        return cast(QColormapLineEdit, super().lineEdit())


class _CmapNameDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo = CmapCatalogComboBox()

        # self.combo.addItems(sorted(catalog))
        B = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        btns = QDialogButtonBox(B)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.combo)
        layout.addWidget(btns)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

    def colormap(self) -> Colormap | None:
        return self.combo.currentColormap()
