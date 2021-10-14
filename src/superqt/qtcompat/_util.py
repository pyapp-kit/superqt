import warnings
from enum import EnumMeta
from importlib import import_module

from PyQt6.sip import wrappertype


# Scoped Enum helper
class ScopedEnumMeta(wrappertype):
    def __new__(mcls, name, bases, attrs, **kwargs):
        obj = getattr(import_module(attrs["__module__"]), attrs["__qualname__"])
        cls = super().__new__(mcls, name, (obj,), attrs)
        cls._enums = {}
        for e in obj.__dict__.values():
            if isinstance(e, EnumMeta):
                cls._enums.update(e.__members__)
        return cls

    def __getattr__(cls, key):
        if key in cls._enums:
            member = cls._enums[key]
            warnings.warn(
                "Since Qt 5.12, unscoped Enum access is deprecated\n"
                f"Please use 'Qt.{type(member).__name__}.{key}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return member
        raise AttributeError(f"type object { cls.__name__!r} has no attribute {key!r}")
