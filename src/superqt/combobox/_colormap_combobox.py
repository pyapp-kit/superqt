from __future__ import annotations

import warnings
from contextlib import suppress
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any, Container, Sequence, cast

try:
    from cmap import Colormap

    from superqt.utils._draw_cmap import draw_colormap
except ImportError as e:
    raise ImportError(
        "cmap is required to use `QColormapComboBox`.  Install it with "
        "`pip install cmap` or `pip install superqt[cmap]`."
    ) from e


from qtpy.QtCore import (
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRect,
    QSize,
    Qt,
    Signal,
)
from qtpy.QtGui import (
    QColor,
    QPainter,
    QPaintEvent,
    QPalette,
)
from qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QSizePolicy,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)

from superqt.utils import signals_blocked

if TYPE_CHECKING:
    from cmap._catalog import Category
    from cmap._colormap import ColorStopsLike, Interpolation


CMAP_ROLE = Qt.ItemDataRole.UserRole + 1


class InvalidPolicy(IntEnum):
    """Policy for handling invalid colors."""

    Ignore = auto()
    Warn = auto()
    Raise = auto()


class CmapLineEdit(QLineEdit):
    """A line edit that shows the parent ComboBox popup when clicked."""

    def __init__(
        self, parent: QWidget | None = None, show_combo_on_click: bool = False
    ) -> None:
        super().__init__(parent)
        self.show_combo_on_click = show_combo_on_click

        self._colormap_fraction: float = 1
        self._cmap: Colormap | None = None

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textChanged.connect(self.setColormap)

    def mouseReleaseEvent(self, _: Any) -> None:
        """Show parent popup when clicked.

        Without this, only the down arrow will show the popup.  And if mousePressEvent
        is used instead, the popup will show and then immediately hide.
        """
        parent = self.parent()
        if hasattr(parent, "showPopup") and self.show_combo_on_click:
            parent.showPopup()

    def setColormap(self, cmap: Colormap | str) -> None:
        self._cmap = _try_cast_colormap(cmap)
        palette = self.palette()
        if self._cmap:
            # set self font color to contrast with the colormap
            text = _pick_font_color(self._cmap)
            # don't draw the background (cmap will be drawn in paintEvent)
            base = Qt.GlobalColor.transparent
        else:
            # restore defaults
            pal = par.palette() if (par := self.parent()) else QApplication.palette()
            text = pal.color(QPalette.ColorRole.Text)
            base = pal.color(QPalette.ColorRole.Base)
        palette.setColor(QPalette.ColorRole.Text, text)
        palette.setColor(palette.ColorRole.Base, base)
        self.setPalette(palette)

    def paintEvent(self, e: QPaintEvent) -> None:
        if not self._cmap:
            super().paintEvent(e)
            return

        if self._colormap_fraction > 0.9:
            draw_colormap(self, self._cmap)
            super().paintEvent(e)  # draw text (must come after draw_colormap)
            return

        cmap_rect = self.rect()
        cmap_rect.setWidth(int(cmap_rect.width() * self._colormap_fraction))
        draw_colormap(self, self._cmap, cmap_rect)

        text_rect = QRect(self.rect())
        text_rect.adjust(cmap_rect.width() + 6, 0, -2, 0)
        p = QPainter(self)
        p.setPen(Qt.GlobalColor.black)
        p.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.text(),
        )


class ColormapItemDelegate(QStyledItemDelegate):
    """Delegate that draws colormaps in the ComboBox dropdown."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._item_size: QSize = QSize(80, 22)
        self._colormap_fraction: float = 1
        self._padding: int = 0
        self._border_color: QColor | None = QColor(Qt.GlobalColor.lightGray)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        return super().sizeHint(option, index).expandedTo(self._item_size)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        rect = cast("QRect", option.rect)  # type: ignore
        selected = option.state & QStyle.StateFlag.State_Selected  # type: ignore
        text = index.data(Qt.ItemDataRole.DisplayRole)

        colormap: Colormap | None = index.data(CMAP_ROLE)
        if not colormap:
            colormap = _try_cast_colormap(text)
        if not colormap:
            super().paint(painter, option, index)
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect.adjust(self._padding, self._padding, -self._padding, -self._padding)
        cmap_rect = QRect(rect)
        if self._colormap_fraction < 1:
            cmap_rect.setWidth(int(rect.width() * self._colormap_fraction))

        lighter = 110 if selected else 100
        border = self._border_color if selected else None
        draw_colormap(
            painter, colormap, cmap_rect, lighter=lighter, border_color=border
        )

        # # make new rect with the remaining space
        text_rect = QRect(rect)

        if self._colormap_fraction > 0.9:
            text_align = Qt.AlignmentFlag.AlignCenter
            alpha = 230 if selected else 140
            text_color = _pick_font_color(colormap, alpha=alpha)
        else:
            text_align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            text_color = QColor(Qt.GlobalColor.black)

            text_rect.adjust(
                cmap_rect.width() + self._padding + 4, 0, -self._padding - 2, 0
            )

        painter.setPen(text_color)
        painter.drawText(text_rect, text_align, text)


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

        self.setLineEdit(CmapLineEdit(self))
        self.setItemDelegate(ColormapItemDelegate())

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
        if (_cmap := _try_cast_colormap(cmap)) is None:
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
        idx = self.findData(_try_cast_colormap(color), CMAP_ROLE)
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

    def lineEdit(self) -> CmapLineEdit:
        return cast(CmapLineEdit, super().lineEdit())


class CmapCatalogComboBox(QComboBox):
    """A combo box for selecting a colormap from the entire cmap catalog.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget.
    prefer_short_names : bool, optional
        If True (default), short names (without the namespace prefix) will be
        preferred over fully qualified names. In cases where the same short name is
        used in multiple namespaces, they will *all* be referred to by their fully
        qualified (namespaced) name.
    categories : Container[Category], optional
        If provided, only return names from the given categories.
    interpolation : Interpolation, optional
        If provided, only return names that have the given interpolation method.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        categories: Container[Category] = (),
        prefer_short_names: bool = True,
        interpolation: Interpolation | None = None,
    ) -> None:
        super().__init__(parent)

        # get valid names according to preferences
        word_list = sorted(
            Colormap.catalog().unique_keys(
                prefer_short_names=prefer_short_names,
                categories=categories,
                interpolation=interpolation,
            )
        )

        # initialize the combobox
        self.addItems(word_list)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setEditable(True)
        self.setDuplicatesEnabled(False)
        # (must come before setCompleter)
        self.setLineEdit(CmapLineEdit(self))

        # setup the completer
        completer = QCompleter(word_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setModel(self.model())
        self.setCompleter(completer)

        # set the delegate for both the popup and the combobox
        delegate = ColormapItemDelegate()
        completer.popup().setItemDelegate(delegate)
        self.setItemDelegate(delegate)

    def currentColormap(self) -> Colormap | None:
        """Returns the currently selected Colormap or None if not yet selected."""
        return _try_cast_colormap(self.currentText())


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


def _try_cast_colormap(val: Any) -> Colormap | None:
    if isinstance(val, Colormap):
        return val
    with suppress(Exception):
        return Colormap(val)
    return None


def _pick_font_color(cmap: Colormap, at_stop: float = 0.49, alpha: int = 255) -> QColor:
    """Pick a font shade that contrasts with the given color."""
    if _is_dark(cmap, at_stop):
        return QColor(0, 0, 0, alpha)
    else:
        return QColor(255, 255, 255, alpha)


def _is_dark(cmap: Colormap, at_stop: float, threshold: float = 110) -> bool:
    color = cmap(at_stop)
    r, g, b, a = color.rgba8
    return (r * 0.299 + g * 0.587 + b * 0.114) > threshold
