from __future__ import annotations

from cmap import Colormap
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon, QPainter, QPaintEvent, QPalette
from qtpy.QtWidgets import QApplication, QLineEdit, QStyle, QWidget

from ._cmap_utils import draw_colormap, pick_font_color, try_cast_colormap

MISSING = QStyle.StandardPixmap.SP_TitleBarContextHelpButton


class QColormapLineEdit(QLineEdit):
    """A QLineEdit that shows a colormap swatch.

    When the current text is a valid colormap name from the `cmap` package, a swatch
    of the colormap will be shown to the left of the text (if `fractionalColormapWidth`
    is less than .75) or behind the text (for when the colormap fills the full width).

    If the current text is not a valid colormap name, a swatch of the fallback colormap
    will be shown instead (by default, a gray colormap) if `fractionalColormapWidth` is
    less than .75.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        fractional_colormap_width: float = 0.35,
        fallback_cmap: Colormap | str | None = "gray",
        missing_icon: QIcon | QStyle.StandardPixmap = MISSING,
    ) -> None:
        super().__init__(parent)
        self.setFractionalColormapWidth(fractional_colormap_width)
        self.setMissingColormap(fallback_cmap)

        if isinstance(missing_icon, QStyle.StandardPixmap):
            self._missing_icon: QIcon = self.style().standardIcon(missing_icon)
        elif isinstance(missing_icon, QIcon):
            self._missing_icon = missing_icon
        else:
            raise TypeError("missing_icon must be a QIcon or QStyle.StandardPixmap")

        # don't draw the background
        # otherwise it will cover the colormap during super().paintEvent
        palette = self.palette()
        palette.setColor(palette.ColorRole.Base, Qt.GlobalColor.transparent)
        self.setPalette(palette)

        self._cmap: Colormap | None = None  # current colormap
        self.textChanged.connect(self.setColormap)

    def setFractionalColormapWidth(self, fraction: float) -> None:
        self._colormap_fraction: float = float(fraction)
        align = Qt.AlignmentFlag.AlignVCenter
        if self._cmap_is_full_width():
            align |= Qt.AlignmentFlag.AlignCenter
        else:
            align |= Qt.AlignmentFlag.AlignLeft
        self.setAlignment(align)

    def fractionalColormapWidth(self) -> float:
        return self._colormap_fraction

    def setMissingColormap(self, cmap: Colormap | str | None) -> None:
        self._missing_cmap: Colormap | None = try_cast_colormap(cmap)

    def colormap(self) -> Colormap | None:
        return self._cmap

    def setColormap(self, cmap: Colormap | str | None) -> None:
        self._cmap = try_cast_colormap(cmap)

        # set self font color to contrast with the colormap
        if self._cmap and self._cmap_is_full_width():
            text = pick_font_color(self._cmap)
        else:
            text = QApplication.palette().color(QPalette.ColorRole.Text)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Text, text)
        self.setPalette(palette)

    def _cmap_is_full_width(self):
        return self._colormap_fraction >= 0.75

    def paintEvent(self, e: QPaintEvent) -> None:
        cmap_rect = self.rect()
        cmap_rect.setWidth(int(cmap_rect.width() * self._colormap_fraction))

        left_margin = 6
        if not self._cmap_is_full_width():
            # leave room for the colormap
            left_margin += cmap_rect.width()
        self.setTextMargins(left_margin, 2, 0, 0)

        if self._cmap:
            draw_colormap(self, self._cmap, cmap_rect)
        elif not self._cmap_is_full_width():
            if self._missing_cmap:
                draw_colormap(self, self._missing_cmap, cmap_rect)
            self._missing_icon.paint(QPainter(self), cmap_rect.adjusted(4, 4, 0, -4))

        super().paintEvent(e)  # draw text (must come after draw_colormap)

    # def mouseReleaseEvent(self, _: Any) -> None:
    #     """Show parent popup when clicked.

    #     Without this, only the down arrow will show the popup.  And if mousePressEvent
    #     is used instead, the popup will show and then immediately hide.
    #     """
    #     parent = self.parent()
    #     if hasattr(parent, "showPopup") and self.show_combo_on_click:
    #         parent.showPopup()
