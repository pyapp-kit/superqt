from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qtpy.QtCore import QRect, Qt
from qtpy.QtGui import QPainter, QPaintEvent, QPalette
from qtpy.QtWidgets import QApplication, QLineEdit, QWidget

from ._cmap_utils import draw_colormap, pick_font_color, try_cast_colormap

if TYPE_CHECKING:
    from cmap import Colormap


class QColormapLineEdit(QLineEdit):
    """A line edit that shows the parent ComboBox popup when clicked."""

    def __init__(
        self, parent: QWidget | None = None, show_combo_on_click: bool = False
    ) -> None:
        super().__init__(parent)
        self.show_combo_on_click = show_combo_on_click

        self._colormap_fraction: float = 0.35
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

    def colormap(self) -> Colormap | None:
        return self._cmap

    def setColormap(self, cmap: Colormap | str | None) -> None:
        self._cmap = try_cast_colormap(cmap)
        palette = self.palette()
        if self._cmap:
            # set self font color to contrast with the colormap
            text = pick_font_color(self._cmap)
            # don't draw the background (cmap will be drawn in paintEvent)
            base = Qt.GlobalColor.transparent
        else:
            # restore defaults
            if (par := self.parent()) and hasattr(par, "palette"):
                pal = par.palette()
            else:
                pal = QApplication.palette()
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
