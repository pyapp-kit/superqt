from abc import ABCMeta, abstractmethod
from enum import Enum, EnumMeta


class ABCEnumMeta(EnumMeta, ABCMeta):
    ...


# This class isn't actually used internally anywhere, but it makes for a good
# FontEnum template.  The one critical method is _font_file()... which must return
# a string path to the OTF or TTF file containing the fonts.
class FontEnum(Enum, metaclass=ABCEnumMeta):
    @classmethod
    @abstractmethod
    def _font_file(cls) -> str:
        """The path location of an OTF or TTF font file."""
        ...

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
