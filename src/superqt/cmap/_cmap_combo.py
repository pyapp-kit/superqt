from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from cmap import Colormap
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QButtonGroup,
    QCheckBox,
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


class QColormapComboBox(QComboBox):
    """A drop down menu for selecting colors.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget.
    allow_user_colormaps : bool, optional
        Whether the user can add custom colormaps by clicking the "Add
        Colormap..." item. Default is False. Can also be set with
        `setUserAdditionsAllowed`.
    add_colormap_text: str, optional
        The text to display for the "Add Colormap..." item.
        Default is "Add Colormap...".
    """

    currentColormapChanged = Signal(Colormap)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        allow_user_colormaps: bool = False,
        add_colormap_text: str = "Add Colormap...",
    ) -> None:
        # init QComboBox
        super().__init__(parent)
        self._add_color_text: str = add_colormap_text
        self._allow_user_colors: bool = allow_user_colormaps
        self._last_cmap: Colormap | None = None

        self.setLineEdit(_PopupColormapLineEdit(self))
        self.lineEdit().setReadOnly(True)
        self.setItemDelegate(QColormapItemDelegate(self))

        self.currentIndexChanged.connect(self._on_index_changed)
        # there's a little bit of a potential bug here:
        # if the user clicks on the "Add Colormap..." item
        # then an indexChanged signal will be emitted, but it may not
        # actually represent a "true" change in the index if they dismiss the dialog
        self.activated.connect(self._on_activated)

        self.setUserAdditionsAllowed(allow_user_colormaps)

    def userAdditionsAllowed(self) -> bool:
        """Returns whether the user can add custom colors."""
        return self._allow_user_colors

    def setUserAdditionsAllowed(self, allow: bool) -> None:
        """Sets whether the user can add custom colors.

        If enabled, an "Add Colormap..." item will be added to the end of the
        list. When clicked, a dialog will be shown to allow the user to select
        a colormap from the
        [cmap catalog](https://cmap-docs.readthedocs.io/en/latest/catalog/).
        """
        self._allow_user_colors = bool(allow)

        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx < 0:
            if self._allow_user_colors:
                self.addItem(self._add_color_text)
        elif not self._allow_user_colors:
            self.removeItem(idx)

    def clear(self) -> None:
        super().clear()
        self.setUserAdditionsAllowed(self._allow_user_colors)

    def itemColormap(self, index: int) -> Colormap | None:
        """Returns the color of the item at the given index."""
        return self.itemData(index, CMAP_ROLE)

    def addColormap(self, cmap: ColorStopsLike) -> None:
        """Adds the colormap to the QComboBox."""
        if (_cmap := try_cast_colormap(cmap)) is None:
            raise ValueError(f"Invalid colormap value: {cmap!r}")

        for i in range(self.count()):
            if item := self.itemColormap(i):
                if item.name == _cmap.name:
                    return  # no duplicates  # pragma: no cover

        had_items = self.count() > int(self._allow_user_colors)
        # add the new color and set the background color of that item
        self.addItem(_cmap.name.rsplit(":", 1)[-1])
        self.setItemData(self.count() - 1, _cmap, CMAP_ROLE)
        if not had_items:  # first item added
            self._on_index_changed(self.count() - 1)

        # make sure the "Add Colormap..." item is last
        idx = self.findData(self._add_color_text, Qt.ItemDataRole.DisplayRole)
        if idx >= 0:
            with signals_blocked(self):
                self.removeItem(idx)
                self.addItem(self._add_color_text)

    def addColormaps(self, colors: Sequence[Any]) -> None:
        """Adds colors to the QComboBox."""
        for color in colors:
            self.addColormap(color)

    def currentColormap(self) -> Colormap | None:
        """Returns the currently selected Colormap or None if not yet selected."""
        return self.currentData(CMAP_ROLE)

    def setCurrentColormap(self, color: Any) -> None:
        """Adds the color to the QComboBox and selects it."""
        if not (cmap := try_cast_colormap(color)):
            raise ValueError(f"Invalid colormap value: {color!r}")

        for idx in range(self.count()):
            if (item := self.itemColormap(idx)) and item.name == cmap.name:
                self.setCurrentIndex(idx)

    def _on_activated(self, index: int) -> None:
        if self.itemText(index) != self._add_color_text:
            return

        dlg = _CmapNameDialog(self, Qt.WindowType.Sheet)
        if dlg.exec() and (cmap := dlg.combo.currentColormap()):
            # add the color and select it, without adding duplicates
            for i in range(self.count()):
                if (item := self.itemColormap(i)) and cmap.name == item.name:
                    self.setCurrentIndex(i)
                    return
            self.addColormap(cmap)
            self.currentIndexChanged.emit(self.currentIndex())
        elif self._last_cmap is not None:
            # user canceled, restore previous color without emitting signal
            idx = self.findData(self._last_cmap, CMAP_ROLE)
            if idx >= 0:
                with signals_blocked(self):
                    self.setCurrentIndex(idx)

    def _on_index_changed(self, index: int) -> None:
        colormap = self.itemData(index, CMAP_ROLE)
        if isinstance(colormap, Colormap):
            self.currentColormapChanged.emit(colormap)
            self.lineEdit().setColormap(colormap)
            self._last_cmap = colormap


CATEGORIES = ("sequential", "diverging", "cyclic", "qualitative", "miscellaneous")


class _CmapNameDialog(QDialog):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)

        self.combo = CmapCatalogComboBox()

        B = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        btns = QDialogButtonBox(B)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.combo)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(False)
        for cat in CATEGORIES:
            box = QCheckBox(cat)
            self._btn_group.addButton(box)
            box.setChecked(True)
            box.toggled.connect(self._on_check_toggled)
            layout.addWidget(box)

        layout.addWidget(btns)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.resize(self.sizeHint())

    def _on_check_toggled(self) -> None:
        # get valid names according to preferences
        word_list = Colormap.catalog().unique_keys(
            prefer_short_names=True,
            categories={b.text() for b in self._btn_group.buttons() if b.isChecked()},
        )
        self.combo.clear()
        self.combo.addItems(sorted(word_list))


class _PopupColormapLineEdit(QColormapLineEdit):
    def mouseReleaseEvent(self, _: Any) -> None:
        """Show parent popup when clicked.

        Without this, only the down arrow will show the popup.  And if mousePressEvent
        is used instead, the popup will show and then immediately hide.
        """
        parent = self.parent()
        if parent and hasattr(parent, "showPopup"):
            parent.showPopup()
