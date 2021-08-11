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
from enum import EnumMeta
from typing import TYPE_CHECKING, Dict

from ._animations import spin, step
from ._qfont_icon import QFontIconFactory
from ._utils import is_font_enum_member, is_font_enum_type

if TYPE_CHECKING:
    # known Plugins (here for IDE autocompletion when importing from superqt)
    from fonticon_fa5 import FA5Brands, FA5Regular, FA5Solid  # type: ignore # noqa
    from fonticon_fthr4 import Feather4  # type: ignore # noqa
    from fonticon_lnr import Linearicons  # type: ignore # noqa
    from fonticon_mdi5 import MDI5  # type: ignore # noqa

    from superqt.qtcompat.QtGui import QFont, QIcon
    from superqt.qtcompat.QtWidgets import QWidget


ENTRY_POINT = "superqt.fonticon"
_FONT_LIBRARY: Dict[str, EnumMeta] = {}
_FONT_KEYS: Dict[str, EnumMeta] = {}
_FACTORY_INSTANCE = None


def _font_factory() -> QFontIconFactory:
    global _FACTORY_INSTANCE
    if _FACTORY_INSTANCE is None:
        _FACTORY_INSTANCE = QFontIconFactory()
    return _FACTORY_INSTANCE


def icon(*args, **kwargs) -> "QIcon":
    return _font_factory().icon(*args, **kwargs)


def font(*args, **kwargs) -> "QFont":
    return _font_factory().font(*args, **kwargs)


def setTextIcon(wdg: "QWidget", font, size=None) -> None:
    return _font_factory().setTextIcon(wdg, font, size)


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
        else:
            warnings.warn(
                f"Object {cls} loaded from plugin {ep.value!r} is not a valid font enum"
            )


def __getattr__(name):
    if name not in _FONT_LIBRARY:
        discover_fonts()
    try:
        return _FONT_LIBRARY[name]
    except KeyError:
        msg = f"module {__name__!r} has no attribute {name!r}. You may need to install it."
        if _FONT_LIBRARY:
            msg += f" Available FontEnums include: {set(_FONT_LIBRARY)}"
        raise AttributeError(msg)
