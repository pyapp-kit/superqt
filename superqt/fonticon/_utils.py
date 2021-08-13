from __future__ import annotations

from enum import Enum, EnumMeta
from inspect import ismethod
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    # a FontEnum is an Enum with a classmethod called `_font_file`
    # (it's hard to use typing.Protocol combined with Enum)
    class FontEnum(Enum):
        @classmethod
        def _font_file(cls) -> str:
            ...


def is_font_enum_type(obj) -> bool:
    """Return True if `obj` is a font enum capable of creating icons."""
    return (
        hasattr(obj, "_font_file")
        and ismethod(obj._font_file)
        and isinstance(obj, EnumMeta)
    )


def ensure_font_enum_type(obj) -> type[FontEnum]:
    if is_font_enum_type(type(obj)):
        return type(cast("FontEnum", obj))
    if not is_font_enum_type(obj):
        raise TypeError(
            "must be either a string, or an Enum object with a "
            "'_font_file' method that returns a file path to a font file. "
            f"got: {type(obj)}"
        )
    return obj


def str2enum(key: str) -> FontEnum:
    """Get a registered FontEnum member for a given string key.

    For instance, if the fonticon_fa5 package is installed:
    'fa5s.bath' -> fonticon_fa5.FA5Solid.bath
    """
    from . import _FONT_KEYS, _discover_fonts

    key, glyph = key.split(".")
    if key not in _FONT_KEYS:
        _discover_fonts()
    try:
        fontenum = _FONT_KEYS[key]
    except KeyError:
        raise ValueError(
            f"Unrecognized font key: {key}. Registered keys: {list(_FONT_KEYS)}"
        )
    return _find_glyphname(fontenum, glyph)


def _find_glyphname(enumclass: EnumMeta, glyphname: str) -> FontEnum:
    """Given a font enum class, find a glyph name that may be canonicalized"""
    import keyword

    member = getattr(enumclass, glyphname, None)
    if member is not None:
        return member

    _glyph = glyphname
    if glyphname[0].isdigit():
        glyphname = "_" + glyphname

    if keyword.iskeyword(glyphname):
        glyphname += "_"

    glyphname = glyphname.replace("-", "_")

    member = getattr(enumclass, glyphname, None)
    if member is not None:
        return member

    if glyphname != _glyph:
        _glyph += f" or {glyphname}"
    raise ValueError(f"FontEnum {enumclass} has no member: {_glyph}")
