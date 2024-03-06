from __future__ import annotations

from typing import TYPE_CHECKING, cast

from qtpy.QtCore import QModelIndex, QObject, QPersistentModelIndex, QRect, QSize, Qt
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from ._cmap_utils import CMAP_ROLE, draw_colormap, pick_font_color, try_cast_colormap

if TYPE_CHECKING:
    from cmap import Colormap

DEFAULT_SIZE = QSize(80, 22)
DEFAULT_BORDER_COLOR = QColor(Qt.GlobalColor.transparent)


class QColormapItemDelegate(QStyledItemDelegate):
    """Delegate that draws colormaps into a QAbstractItemView item.

    Parameters
    ----------
    parent : QObject, optional
        The parent object.
    item_size : QSize, optional
        The size hint for each item, by default QSize(80, 22).
    fractional_colormap_width : float, optional
        The fraction of the widget width to use for the colormap swatch. If the
        colormap is full width (greater than 0.75), the swatch will be drawn behind
        the text. Otherwise, the swatch will be drawn to the left of the text.
        Default is 0.33.
    padding : int, optional
        The padding (in pixels) around the edge of the item, by default 1.
    checkerboard_size : int, optional
        Size (in pixels) of the checkerboard pattern to draw behind colormaps with
        transparency, by default 4. If 0, no checkerboard is drawn.
    """

    def __init__(
        self,
        parent: QObject | None = None,
        *,
        item_size: QSize = DEFAULT_SIZE,
        fractional_colormap_width: float = 1,
        padding: int = 1,
        checkerboard_size: int = 4,
    ) -> None:
        super().__init__(parent)
        self._item_size = item_size
        self._colormap_fraction = fractional_colormap_width
        self._padding = padding
        self._border_color: QColor | None = DEFAULT_BORDER_COLOR
        self._checkerboard_size = checkerboard_size

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
        self.initStyleOption(option, index)
        rect = cast("QRect", option.rect)  # type: ignore
        selected = option.state & QStyle.StateFlag.State_Selected  # type: ignore
        text = index.data(Qt.ItemDataRole.DisplayRole)
        colormap: Colormap | None = index.data(CMAP_ROLE) or try_cast_colormap(text)

        if not colormap:  # pragma: no cover
            return super().paint(painter, option, index)

        painter.save()
        rect.adjust(self._padding, self._padding, -self._padding, -self._padding)
        cmap_rect = QRect(rect)
        cmap_rect.setWidth(int(rect.width() * self._colormap_fraction))

        lighter = 110 if selected else 100
        border = self._border_color if selected else None
        draw_colormap(
            painter,
            colormap,
            cmap_rect,
            lighter=lighter,
            border_color=border,
            checkerboard_size=self._checkerboard_size,
        )

        # # make new rect with the remaining space
        text_rect = QRect(rect)

        if self._colormap_fraction > 0.75:
            text_align = Qt.AlignmentFlag.AlignCenter
            alpha = 230 if selected else 140
            text_color = pick_font_color(colormap, alpha=alpha)
        else:
            text_align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            text_color = QColor(Qt.GlobalColor.black)
            text_rect.adjust(
                cmap_rect.width() + self._padding + 4, 0, -self._padding - 2, 0
            )

        painter.setPen(text_color)
        # cast to int works all the way back to Qt 5.12...
        # but the enum only works since Qt 5.14
        painter.drawText(text_rect, int(text_align), text)
        painter.restore()
