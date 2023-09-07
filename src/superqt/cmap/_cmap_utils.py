from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any

from cmap import Colormap
from qtpy.QtCore import QRect, QRectF, Qt
from qtpy.QtGui import QColor, QLinearGradient, QPaintDevice, QPainter

if TYPE_CHECKING:
    from cmap._colormap import ColorStopsLike

CMAP_ROLE = Qt.ItemDataRole.UserRole + 1


def draw_colormap(
    painter_or_device: QPainter | QPaintDevice,
    cmap: Colormap | str | ColorStopsLike,
    rect: QRect | QRectF | None = None,
    border_color: QColor | str | None = None,
    border_width: int = 1,
    lighter: int = 100,
) -> None:
    """Draw a colormap onto a QPainter or QPaintDevice.

    Parameters
    ----------
    painter_or_device : QPainter | QPaintDevice
        A `QPainter` instance or a `QPaintDevice` (e.g. a QWidget or QPixmap) onto
        which to paint the colormap.
    cmap : Colormap
        `cmap.Colormap` instance, or anything that can be converted to one (such as a
        string name of a colormap in the `cmap` catalog).
        https://cmap-docs.readthedocs.io/en/latest/colormaps/#colormaplike-objects
    rect : QRect | QRectF | None, optional
        A rect onto which to draw. If `None`, the `painter.viewport()` will be
        used.  by default `None`
    border_color : QColor | str | None
        If not `None`, a border of color `border_color` and width `border_width` is
        included around the edge, by default None.
    border_width : int, optional
        The width of the border to draw (provided `border_color` is not `None`),
        by default 2
    lighter : int, optional
        Percentage by which to lighten (or darken) the colors. Greater than 100
        lightens, less than 100 darkens, by default 100 (i.e. no change).

    Examples
    --------
    ```python
    from qtpy.QtGui import QPixmap
    from qtpy.QtWidgets import QWidget
    from superqt.utils import draw_colormap

    viridis = 'viridis'  # or cmap.Colormap('viridis')

    class W(QWidget):
        def paintEvent(self, event) -> None:
            draw_colormap(self, viridis, event.rect())

    # or draw onto a QPixmap
    pm = QPixmap(200, 200)
    draw_colormap(pm, viridis)
    ```
    """
    if isinstance(painter_or_device, QPainter):
        painter = painter_or_device
    elif isinstance(painter_or_device, QPaintDevice):
        painter = QPainter(painter_or_device)
    else:
        raise TypeError(
            "Expected a QPainter or QPaintDevice instance, "
            f"got {type(painter_or_device)!r} instead."
        )

    if not isinstance(cmap, Colormap):
        try:
            cmap = Colormap(cmap)
        except Exception as e:
            raise TypeError(
                f"Expected a Colormap instance or something that can be "
                f"converted to one, got {type(cmap)!r} instead."
            ) from e

    if rect is None:
        rect = painter.viewport()

    painter.setPen(Qt.PenStyle.NoPen)

    if border_width and border_color is not None:
        # draw rect, and then contract it by border_width
        painter.setBrush(QColor(border_color))
        painter.drawRect(rect)
        rect = rect.adjusted(border_width, border_width, -border_width, -border_width)

    if (
        cmap.interpolation == "nearest"
        or getattr(cmap.color_stops, "_interpolation", "") == "nearest"
    ):
        # XXX: this is a little bit of a hack.
        # when the interpolation is nearest, the last stop is often at 1.0
        # which means that the last color is not drawn.
        # to fix this, we shrink the drawing area slightly
        # it might not work well with unenvenly-spaced stops
        # (but those are uncommon for categorical colormaps)
        width = rect.width() - rect.width() / len(cmap.color_stops)
        for stop in cmap.color_stops:
            painter.setBrush(QColor(stop.color.hex).lighter(lighter))
            painter.drawRect(rect.adjusted(int(stop.position * width), 0, 0, 0))
    else:
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        for stop in cmap.color_stops:
            gradient.setColorAt(stop.position, QColor(stop.color.hex).lighter(lighter))
        painter.setBrush(gradient)
        painter.drawRect(rect)


def try_cast_colormap(val: Any) -> Colormap | None:
    """Try to cast `val` to a Colormap instance, return None if it fails."""
    if isinstance(val, Colormap):
        return val
    with suppress(Exception):
        return Colormap(val)
    return None


def pick_font_color(cmap: Colormap, at_stop: float = 0.49, alpha: int = 255) -> QColor:
    """Pick a font shade that contrasts with the given colormap at `at_stop`."""
    if _is_dark(cmap, at_stop):
        return QColor(0, 0, 0, alpha)
    else:
        return QColor(255, 255, 255, alpha)


def _is_dark(cmap: Colormap, at_stop: float, threshold: float = 110) -> bool:
    """Return True if the color at `at_stop` is dark according to `threshold`."""
    color = cmap(at_stop)
    r, g, b, a = color.rgba8
    return (r * 0.299 + g * 0.587 + b * 0.114) > threshold
