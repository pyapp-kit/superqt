__all__ = ["FontEnum", "is_font_enum_type", "icon", "font", "ENTRY_POINT"]

from typing import TYPE_CHECKING, Dict, Tuple

from ._font_enum import FontEnum, is_font_enum_type
from ._qfont_icon import QFontIcon

if TYPE_CHECKING:
    from superqt.qtcompat.QtGui import QFont, QIcon

    try:
        pass
    except ImportError:
        pass

    try:
        pass
    except ImportError:
        pass


ENTRY_POINT = "superqt.fonticon"


_INSTANCE = None
_FONT_LIBRARY: Dict[str, Tuple[FontEnum, str]] = {}


def _instance() -> QFontIcon:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = QFontIcon()
    return _INSTANCE


def icon(*args, **kwargs) -> "QIcon":
    return _instance().icon(*args, **kwargs)


def font(*args, **kwargs) -> "QFont":
    return _instance().font(*args, **kwargs)


def font_list():
    return list(_FONT_LIBRARY)


def discover_fonts():
    try:
        from importlib.metadata import entry_points
    except ImportError:
        from importlib_metadata import entry_points
    for ep in entry_points().get(ENTRY_POINT, {}):
        try:
            module = ep.load()
        except ImportError:
            continue
        for attr in dir(module):
            obj = getattr(module, attr)
            if is_font_enum_type(obj):
                _FONT_LIBRARY[attr] = obj


def __getattr__(name):
    if name not in _FONT_LIBRARY:
        discover_fonts()
    if name in _FONT_LIBRARY:
        return _FONT_LIBRARY[name]
    msg = f"module {__name__!r} has no attribute {name!r}."
    if _FONT_LIBRARY:
        msg += f" Available FontEnums include: {set(_FONT_LIBRARY)}"
    raise AttributeError(msg)
