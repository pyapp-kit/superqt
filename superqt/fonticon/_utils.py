from enum import Enum, EnumMeta
from inspect import ismethod
from typing import cast


def is_font_enum_type(obj) -> bool:
    """Return True if `obj` is a font enum capable of creating icons."""
    return (
        hasattr(obj, "_font_file")
        and ismethod(obj._font_file)
        and isinstance(obj, EnumMeta)
    )


def is_font_enum_member(obj) -> bool:
    """Return True if `obj` is a font enum member of creating icons."""
    return (
        hasattr(obj, "_font_file")
        and ismethod(obj._font_file)
        and isinstance(obj, Enum)
    )


def ensure_font_enum_type(obj) -> EnumMeta:
    if is_font_enum_member(obj):
        return type(cast(Enum, obj))
    if not is_font_enum_type(obj):
        raise TypeError(
            "must be either a string, or an Enum object with a "
            "'_font_file' method that returns a file path to a font file. "
            f"got: {type(obj)}"
        )
    return obj


def str2enum(key: str) -> Enum:
    from . import _FONT_KEYS, discover_fonts

    key, glyph = key.split(".")
    if key not in _FONT_KEYS:
        discover_fonts()
    try:
        fontenum = _FONT_KEYS[key]
    except KeyError:
        raise ValueError(
            f"Unrecognized font key: {key}. Registered keys: {list(_FONT_KEYS)}"
        )
    return find_glyphname(fontenum, glyph)


def find_glyphname(enumclass: EnumMeta, glyphname: str) -> Enum:
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
