from __future__ import annotations

__all__ = [
    "ENTRY_POINT",
    "font",
    "icon",
    "is_font_enum_type",
    "spin",
    "pulse",
    "IconOptions",
    "str2enum",
]

import warnings
from enum import EnumMeta
from typing import TYPE_CHECKING

from ._animations import Animation, pulse, spin
from ._qfont_icon import DEFAULT_SCALING_FACTOR, IconOptions, QFontIconStore
from ._utils import is_font_enum_type, str2enum

if TYPE_CHECKING:
    # known Plugins (here for IDE autocompletion when importing from superqt)
    from fonticon_bs import Bootstrap  # type: ignore # noqa
    from fonticon_fa5 import FA5Brands, FA5Regular, FA5Solid  # type: ignore # noqa
    from fonticon_fthr4 import Feather4  # type: ignore # noqa
    from fonticon_lnr import Linearicons  # type: ignore # noqa
    from fonticon_mdi5 import MDI5  # type: ignore # noqa

    from superqt.qtcompat.QtGui import QFont, QTransform
    from superqt.qtcompat.QtWidgets import QWidget

    from ._qfont_icon import GlyphKey, QFontIcon, ValidColor

_FONT_LIBRARY: dict[str, EnumMeta] = {}
_FONT_KEYS: dict[str, EnumMeta] = {}
_FACTORY_INSTANCE = None


def _font_factory() -> QFontIconStore:
    global _FACTORY_INSTANCE
    if _FACTORY_INSTANCE is None:
        _FACTORY_INSTANCE = QFontIconStore()
    return _FACTORY_INSTANCE


def icon(
    glyph: GlyphKey,
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


def font_list():
    return list(_FONT_LIBRARY)


def _discover_fonts():
    try:
        from importlib.metadata import entry_points
    except ImportError:
        from importlib_metadata import entry_points  # type: ignore
    for ep in entry_points().get(ENTRY_POINT, {}):
        try:
            cls = ep.load()
        except ImportError as e:
            warnings.warn(f"failed to load fonticon entrypoint: {ep.value}. {e}")
            continue
        if is_font_enum_type(cls):
            _FONT_LIBRARY[cls.__name__] = cls
            _FONT_KEYS[ep.name] = cls
        else:
            warnings.warn(
                f"Object {cls} loaded from plugin {ep.value!r} is not a valid font enum"
            )


def __getattr__(name):
    if name not in _FONT_LIBRARY:
        _discover_fonts()
    try:
        return _FONT_LIBRARY[name]
    except KeyError:
        msg = f"module {__name__!r} has no attribute {name!r}. You may need to install it."
        if _FONT_LIBRARY:
            msg += f" Available FontEnums include: {set(_FONT_LIBRARY)}"
        raise AttributeError(msg)
