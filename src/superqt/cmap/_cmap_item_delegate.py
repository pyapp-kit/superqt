from __future__ import annotations

from typing import cast

from cmap import Colormap
from qtpy.QtCore import QModelIndex, QObject, QPersistentModelIndex, QRect, QSize, Qt
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from ._cmap_utils import CMAP_ROLE, draw_colormap, pick_font_color, try_cast_colormap


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
            colormap = try_cast_colormap(text)
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
            text_color = pick_font_color(colormap, alpha=alpha)
        else:
            text_align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            text_color = QColor(Qt.GlobalColor.black)

            text_rect.adjust(
                cmap_rect.width() + self._padding + 4, 0, -self._padding - 2, 0
            )

        painter.setPen(text_color)
        painter.drawText(text_rect, text_align, text)
