from __future__ import annotations

__all__ = [
    "ENTRY_POINT",
    "font",
    "icon",
    "spin",
    "pulse",
    "IconOptions",
    "IconFont",
    "IconFontMeta",
]

from typing import TYPE_CHECKING, Optional

from ._animations import Animation, pulse, spin
from ._iconfont import IconFont, IconFontMeta
from ._plugins import FontIconManager as _FIM
from ._qfont_icon import DEFAULT_SCALING_FACTOR, IconOptions
from ._qfont_icon import QFontIconStore as _QFIS

if TYPE_CHECKING:
    from superqt.qtcompat.QtGui import QFont, QTransform
    from superqt.qtcompat.QtWidgets import QWidget

    from ._qfont_icon import QFontIcon, ValidColor

ENTRY_POINT = _FIM.ENTRY_POINT


def icon(
    glyph_key: str,
    scale_factor: float = DEFAULT_SCALING_FACTOR,
    color: ValidColor = None,
    opacity: float = 1,
    animation: Optional[Animation] = None,
    transform: Optional[QTransform] = None,
    states: dict[str, dict] = {},
) -> QFontIcon:
    return _QFIS.instance().icon(
        glyph_key,
        scale_factor=scale_factor,
        color=color,
        opacity=opacity,
        animation=animation,
        transform=transform,
        states=states,
    )


def font(font_prefix: str, size: int = None) -> QFont:
    """Create QFont for `font_prefix`

    Parameters
    ----------
    font_prefix : str
        Font_prefix, such as 'fa5s' or 'mdi6', representing a font-family and style.
    size : int, optional
        Size for QFont.  passed to `setPixelSize`, by default None

    Returns
    -------
    QFont
        QFont instance that can be used to add fonticons to widgets.
    """
    return _QFIS.instance().font(font_prefix, size)


def setTextIcon(widget: QWidget, key: str, size: float = None) -> None:
    """Set text on a widget to a specific font & glyph.

    This is an alternative to setting a QIcon with a pixmap.  It may be easier to
    combine with dynamic stylesheets.

    Parameters
    ----------
    wdg : QWidget
        A widget supporting a `setText` method.
    key : str
        The font key encapsulating a font-family, style, and glyph.  For example,
        'fa5s.smile'.
    size : int, optional
        Size for QFont.  passed to `setPixelSize`, by default None
    """
    return _QFIS.instance().setTextIcon(widget, key, size)


del DEFAULT_SCALING_FACTOR
