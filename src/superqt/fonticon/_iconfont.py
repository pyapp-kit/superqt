from typing import Mapping, Type, Union

FONTFILE_ATTR = "__font_file__"


class IconFontMeta(type):
    """IconFont metaclass.

    This updates the value of all class attributes to be prefaced with the class
    name (lowercase), and makes sure that all values are valid characters.

    Examples
    --------
    This metaclass turns the following class:

        class FA5S(metaclass=IconFontMeta):
            __font_file__ = 'path/to/font.otf'
            some_char = 0xfa42

    into this:

        class FA5S:
            __font_file__ = path/to/font.otf'
            some_char = 'fa5s.\ufa42'

    In usage, this means that someone could use `icon(FA5S.some_char)` (provided
    that the FA5S class/namespace has already been registered).  This makes
    IDE attribute checking and autocompletion easier.
    """

    __font_file__: str

    def __new__(cls, name, bases, namespace, **kwargs):
        # make sure this class provides the __font_file__ interface
        ff = namespace.get(FONTFILE_ATTR)
        if not (ff and isinstance(ff, (str, classmethod))):
            raise TypeError(
                f"Invalid Font: must declare {FONTFILE_ATTR!r} attribute or classmethod"
            )

        # update all values to be `key.unicode`
        prefix = name.lower()
        for k, v in list(namespace.items()):
            if k.startswith("__"):
                continue
            char = chr(v) if isinstance(v, int) else v
            if len(char) != 1:
                raise TypeError(
                    "Invalid Font: All fonts values must be a single "
                    f"unicode char. ('{name}.{char}' has length {len(char)}). "
                    "You may use unicode representations: like '\\uf641' or '0xf641'"
                )
            namespace[k] = f"{prefix}.{char}"

        return super().__new__(cls, name, bases, namespace, **kwargs)


class IconFont(metaclass=IconFontMeta):
    """Helper class that provides a standard way to create an IconFont.

    Examples
    --------

        class FA5S(IconFont):
            __font_file__ = '...'
            some_char = 0xfa42
    """

    __slots__ = ()
    __font_file__ = "..."


def namespace2font(namespace: Union[Mapping, Type], name: str) -> Type[IconFont]:
    """Convenience to convert a namespace (class, module, dict) into an IconFont."""
    if isinstance(namespace, type):
        assert isinstance(
            getattr(namespace, FONTFILE_ATTR), str
        ), "Not a valid font type"
        return namespace  # type: ignore
    elif hasattr(namespace, "__dict__"):
        ns = dict(namespace.__dict__)
    else:
        raise ValueError(
            "namespace must be a mapping or an object with __dict__ attribute."
        )
    if not str.isidentifier(name):
        raise ValueError(f"name {name!r} is not a valid identifier.")
    return type(name, (IconFont,), ns)
