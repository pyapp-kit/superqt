__all__ = ["FontEnum", "is_font_enum_type", "icon", "font", "ENTRY_POINT"]

from typing import TYPE_CHECKING, Dict, Tuple

from ._font_enum import FontEnum, is_font_enum_type
from ._qfont_icon import QFontIcon

if TYPE_CHECKING:
    from superqt.qtcompat.QtGui import QFont, QIcon


ENTRY_POINT = "superqt_fonticon"


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
    import entrypoints

    for ep_name, ep in entrypoints.get_group_named(ENTRY_POINT).items():
        module = ep.load()
        for attr in dir(module):
            obj = getattr(module, attr)
            if is_font_enum_type(obj):
                _FONT_LIBRARY[attr] = (obj, ep_name)


def __getattr__(name):
    if name not in _FONT_LIBRARY:
        discover_fonts()
    if name in _FONT_LIBRARY:
        return _FONT_LIBRARY[name][0]
    msg = f"module {__name__!r} has no attribute {name!r}."
    if _FONT_LIBRARY:
        msg += f" Available FontEnums include: {set(_FONT_LIBRARY)}"
    raise AttributeError(msg)
