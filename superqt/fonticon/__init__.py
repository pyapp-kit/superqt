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

from typing import TYPE_CHECKING

from ._animations import Animation, pulse, spin
from ._iconfont import IconFont, IconFontMeta
from ._plugins import FontIconManager as _FIM
from ._qfont_icon import DEFAULT_SCALING_FACTOR, IconOptions, QFontIconStore

ENTRY_POINT = _FIM.ENTRY_POINT

if TYPE_CHECKING:

    from superqt.qtcompat.QtGui import QFont, QTransform
    from superqt.qtcompat.QtWidgets import QWidget

    from ._qfont_icon import QFontIcon, ValidColor


_FACTORY_INSTANCE = None


def _font_factory() -> QFontIconStore:
    global _FACTORY_INSTANCE
    if _FACTORY_INSTANCE is None:
        _FACTORY_INSTANCE = QFontIconStore()
    return _FACTORY_INSTANCE


def icon(
    glyph: str,
    scale_factor: float = DEFAULT_SCALING_FACTOR,
    color: ValidColor = None,
    opacity: float = None,
    animation: Animation | None = None,
    transform: QTransform | None = None,
    states: dict[str, dict] = {},
) -> QFontIcon:
    return _font_factory().icon(**locals())


def font(*args, **kwargs) -> QFont:
    return _font_factory().font(*args, **kwargs)


def setTextIcon(wdg: QWidget, font, size=None) -> None:
    return _font_factory().setTextIcon(wdg, font, size)
