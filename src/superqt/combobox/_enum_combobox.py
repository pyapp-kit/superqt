import sys
from enum import Enum, EnumMeta, Flag
from functools import reduce
from itertools import combinations
from operator import or_
from typing import Optional, TypeVar

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QComboBox

EnumType = TypeVar("EnumType", bound=Enum)


NONE_STRING = "----"


def _get_name(enum_value: Enum):
    """Create human readable name if user does not implement `__str__`."""
    str_module = getattr(enum_value.__str__, "__module__", "enum")
    if str_module != "enum" and not str_module.startswith("shibokensupport"):
        # check if function was overloaded
        name = str(enum_value)
    else:
        if enum_value.name is None:
            # This is hack for python bellow 3.11
            if not isinstance(enum_value, Flag):
                raise TypeError(
                    f"Expected Flag instance, got {enum_value}"
                )  # pragma: no cover
            if sys.version_info >= (3, 11):
                # There is a bug in some releases of Python 3.11 (for example 3.11.3)
                # that leads to wrong evaluation of or operation on Flag members
                # and produces numeric value without proper set name property.
                return f"{enum_value.value}"

            # Before python 3.11 there is no smart name set during
            # the creation of Flag members.
            # We needs to decompose the value to get the name.
            # It is under if condition because it uses private API.

            from enum import _decompose

            members, not_covered = _decompose(enum_value.__class__, enum_value.value)
            name = "|".join(m.name.replace("_", " ") for m in members[::-1])
        else:
            name = enum_value.name.replace("_", " ")
    return name


def _get_name_with_value(enum_value: Enum) -> tuple[str, Enum]:
    return _get_name(enum_value), enum_value


class QEnumComboBox(QComboBox):
    """ComboBox presenting options from a python Enum.

    If the Enum class does not implement `__str__` then a human readable name
    is created from the name of the enum member, replacing underscores with spaces.
    """

    currentEnumChanged = Signal(object)

    def __init__(
        self, parent=None, enum_class: Optional[EnumMeta] = None, allow_none=False
    ):
        super().__init__(parent)
        self._enum_class = None
        self._allow_none = False
        if enum_class is not None:
            self.setEnumClass(enum_class, allow_none)
        self.currentIndexChanged.connect(self._emit_signal)

    def setEnumClass(self, enum: Optional[EnumMeta], allow_none=False):
        """Set enum class from which members value should be selected."""
        self.clear()
        self._enum_class = enum
        self._allow_none = allow_none and enum is not None
        if allow_none:
            super().addItem(NONE_STRING)
        names_ = self._get_enum_member_list(enum)
        super().addItems(list(names_))

    @staticmethod
    def _get_enum_member_list(enum: Optional[EnumMeta]):
        if issubclass(enum, Flag):
            members = list(enum.__members__.values())
            comb_list = []
            for i in range(len(members)):
                comb_list.extend(reduce(or_, x) for x in combinations(members, i + 1))

        else:
            comb_list = list(enum.__members__.values())
        return dict(map(_get_name_with_value, comb_list))

    def enumClass(self) -> Optional[EnumMeta]:
        """Return current Enum class."""
        return self._enum_class

    def isOptional(self) -> bool:
        """Return if current enum is with optional annotation."""
        return self._allow_none

    def clear(self):
        self._enum_class = None
        self._allow_none = False
        super().clear()

    def currentEnum(self) -> Optional[EnumType]:
        """Current value as Enum member."""
        if self._enum_class is not None:
            if self._allow_none:
                if self.currentText() == NONE_STRING:
                    return None
            return self._get_enum_member_list(self._enum_class)[self.currentText()]
        return None

    def setCurrentEnum(self, value: Optional[EnumType]) -> None:
        """Set value with Enum."""
        if self._enum_class is None:
            raise RuntimeError(
                "Uninitialized enum class. Use `setEnumClass` before `setCurrentEnum`."
            )
        if value is None and self._allow_none:
            self.setCurrentIndex(0)
            return
        if not isinstance(value, self._enum_class):
            raise TypeError(
                "setValue(self, Enum): argument 1 has unexpected type "
                f"{type(value).__name__!r}"
            )
        self.setCurrentText(_get_name(value))

    def _emit_signal(self):
        if self._enum_class is not None:
            self.currentEnumChanged.emit(self.currentEnum())

    def insertItems(self, *_, **__):
        raise RuntimeError("EnumComboBox does not allow to insert items")

    def insertItem(self, *_, **__):
        raise RuntimeError("EnumComboBox does not allow to insert item")

    def addItems(self, *_, **__):
        raise RuntimeError("EnumComboBox does not allow to add items")

    def addItem(self, *_, **__):
        raise RuntimeError("EnumComboBox does not allow to add item")

    def setInsertPolicy(self, policy):
        raise RuntimeError("EnumComboBox does not allow to insert item")
