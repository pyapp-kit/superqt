__all__ = [
    "is_font_enum_type",
    "is_font_enum_member",
    "icon",
    "font",
    "spin",
    "step",
    "ENTRY_POINT",
]

import warnings
from enum import Enum
from typing import TYPE_CHECKING, Dict

from ._qfont_icon import QFontIcon, is_font_enum_member, is_font_enum_type, spin, step

if TYPE_CHECKING:
    # Plugins
    from fonticon_fa5 import FA5Brands, FA5Regular, FA5Solid  # type: ignore # noqa
    from fonticon_lnr import Linearicons  # type: ignore # noqa
    from fonticon_mdi5 import MDI5  # type: ignore # noqa

    from superqt.qtcompat.QtGui import QFont, QIcon
    from superqt.qtcompat.QtWidgets import QWidget


ENTRY_POINT = "superqt.fonticon"
_INSTANCE = None
_FONT_LIBRARY: Dict[str, Enum] = {}
_FONT_KEYS: Dict[str, Enum] = {}


def _qfont_instance() -> QFontIcon:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = QFontIcon()
    return _INSTANCE


def icon(*args, **kwargs) -> "QIcon":
    return _qfont_instance().icon(*args, **kwargs)


def setTextIcon(wdg: "QWidget", font, size=None):
    return _qfont_instance().setTextIcon(wdg, font, size)


def font(*args, **kwargs) -> "QFont":
    return _qfont_instance().font(*args, **kwargs)


def font_list():
    return list(_FONT_LIBRARY)


def discover_fonts():
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


def __getattr__(name):
    if name not in _FONT_LIBRARY:
        discover_fonts()
    if name in _FONT_LIBRARY:
        return _FONT_LIBRARY[name]
    msg = f"module {__name__!r} has no attribute {name!r}."
    if _FONT_LIBRARY:
        msg += f" Available FontEnums include: {set(_FONT_LIBRARY)}"
    raise AttributeError(msg)
