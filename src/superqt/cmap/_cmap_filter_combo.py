from __future__ import annotations

from typing import TYPE_CHECKING, Any

from cmap import Colormap
from qtpy.QtCore import QSortFilterProxyModel, QStringListModel, Qt, Signal
from qtpy.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from superqt.utils import signals_blocked

from ._catalog_combo import CmapCatalogComboBox
from ._cmap_combo import _CmapNameDialog
from ._cmap_item_delegate import QColormapItemDelegate
from ._cmap_line_edit import QColormapLineEdit
from ._cmap_utils import try_cast_colormap

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cmap._colormap import ColorStopsLike
    from qtpy.QtGui import QKeyEvent


CMAP_ROLE = Qt.ItemDataRole.UserRole + 1


class QColormapFilterComboBox(QComboBox):
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

        # Create line edit and make it editable
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
        # (must come before setCompleter)
        self.setLineEdit(_PopupColormapLineEdit(self))
#        self.setItemDelegate(QColormapItemDelegate(self))

        # use string list model as source model
        self._source_model = QStringListModel(self)
        # Create a proxy model to handle filtering
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._source_model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # Setup completer
        self._completer = QCompleter(self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setModel(self._proxy_model)
        self.setCompleter(self._completer)

        # set the delegate for both the popup and the combobox
        delegate = QColormapItemDelegate()
        if popup := self._completer.popup():
            popup.setItemDelegate(delegate)
        self.setItemDelegate(delegate)

        # Update completer model when items change
        self.model().rowsInserted.connect(self._update_completer_model)
        self.model().rowsRemoved.connect(self._update_completer_model)
        self.currentTextChanged.connect(self._on_text_changed)


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
        self._update_completer_model()
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

        self._update_completer_model()

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

    def _update_completer_model(self) -> None:
        """Update the completer's model with current items."""
        words = []
        for i in range(self.count()):
            if self.itemText(i) != self._add_color_text:
                words.append(self.itemText(i))

        # Ensure we are updating the source model of the proxy
        if isinstance(self._proxy_model.sourceModel(), QStringListModel):
            source_model = self._proxy_model.sourceModel()
            source_model.setStringList(words)  # Update QStringListModel
            self._proxy_model.invalidate()  # Rebuild proxy mapping

    def _on_text_changed(self, text: str) -> None:
        if (cmap := try_cast_colormap(text)) is not None:
            self.currentColormapChanged.emit(cmap)

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        if e and e.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            # select the first completion when pressing enter if the popup is visible
            if (completer := self.completer()) and completer.completionCount():
                self.lineEdit().setText(completer.currentCompletion())  # type: ignore
        return super().keyPressEvent(e)

CATEGORIES = ("sequential", "diverging", "cyclic", "qualitative", "miscellaneous")

class _PopupColormapLineEdit(QColormapLineEdit):
    def mouseReleaseEvent(self, _: Any) -> None:
        """Show parent popup when clicked.

        Without this, only the down arrow will show the popup.  And if mousePressEvent
        is used instead, the popup will show and then immediately hide.
        Also ensure that the popup is not shown when the user selects text.
        """
        if not self.hasSelectedText():
            parent = self.parent()
            if parent and hasattr(parent, "showPopup"):
                parent.showPopup()
