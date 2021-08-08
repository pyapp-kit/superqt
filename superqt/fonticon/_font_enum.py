from abc import ABCMeta, abstractmethod
from enum import Enum, EnumMeta

from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class FontEnumProtocol(Protocol):
    """Basic protocol that FontEnums must follow to work with superqt.fonticons"""

    @classmethod
    def _font_file(cls) -> str:
        ...

    @classmethod
    def _font_family(cls) -> str:
        ...

    @classmethod
    def _font_style(cls) -> str:
        ...


def is_font_enum_type(obj) -> bool:
    """Return True if `obj` is a font enum capable of creating icons."""
    return isinstance(obj, FontEnumProtocol) and isinstance(obj, EnumMeta)


class ABCEnumMeta(EnumMeta, ABCMeta):
    def __dir__(self):
        return (
            [
                "__class__",
                "__doc__",
                "__members__",
                "__module__",
            ]
            + self._member_names_
            + [
                i
                for i in ("_font_file", "_font_family", "_font_style")
                if hasattr(self, i)
            ]
        )


class FontEnum(Enum, metaclass=ABCEnumMeta):
    @classmethod
    @abstractmethod
    def _font_file(cls) -> str:
        """The path location of an OTF or TTF font file."""

    @classmethod
    @abstractmethod
    def _font_family(cls) -> str:
        "Return the font family."

    @classmethod
    @abstractmethod
    def _font_style(cls) -> str:
        "Return the font style.."

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"<{type(self).__name__}.{self.name}: {self.value!r} {self.value} >"

    def __new__(cls, value):
        if isinstance(value, int):
            value = chr(value)
        elif isinstance(value, str):
            if len(value) != 1:
                raise ValueError(
                    f"FontEnum values must be a single character (got {len(value)}). "
                    "You may use unicode representations: like '\\uf641'."
                )
        else:
            raise TypeError("FontEnum values must be a single character or integer.")
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __int__(self):
        return ord(self.value)
