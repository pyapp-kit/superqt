from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from cmap import Colormap
except ImportError as e:
    raise ImportError(
        "cmap is required to use `draw_colormap`.  Install it with `pip install cmap` "
        "or `pip install superqt[cmap]`."
    ) from e

from qtpy.QtCore import QRect, QRectF, Qt
from qtpy.QtGui import QColor, QLinearGradient, QPaintDevice, QPainter

if TYPE_CHECKING:
    from cmap._colormap import ColorStopsLike


def draw_colormap(
    painter_or_device: QPainter | QPaintDevice,
    cmap: Colormap | str | ColorStopsLike,
    rect: QRect | QRectF | None = None,
    border_color: QColor | None = None,
    border_width: int = 2,
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
    border_color : QColor | None, optional
        If not `None`, a border of color `border_color` and width `border_width` is
        included around the edge, by default None.
    border_width : int, optional
        The width of the border to draw (provided `border_color` is not `None`),
        by default 2

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

    if border_width and border_color is not None:
        # draw rect, and then contract it by border_width
        painter.setBrush(border_color)
        painter.drawRect(rect)
        rect = rect.adjusted(border_width, border_width, -border_width, -border_width)

    # no border
    painter.setPen(Qt.PenStyle.NoPen)

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
            painter.setBrush(QColor(stop.color.hex))
            painter.drawRect(rect.adjusted(int(stop.position * width), 0, 0, 0))
    else:
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        for stop in cmap.color_stops:
            gradient.setColorAt(stop.position, QColor(stop.color.hex))
        painter.setBrush(gradient)
        painter.drawRect(rect)
