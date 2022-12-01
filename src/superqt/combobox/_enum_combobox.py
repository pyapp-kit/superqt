from enum import Enum, EnumMeta
from typing import Optional, TypeVar

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QComboBox

EnumType = TypeVar("EnumType", bound=Enum)


NONE_STRING = "----"


def _get_name(enum_value: Enum):
    """Create human readable name if user does not implement `__str__`."""
    if (
        enum_value.__str__.__module__ != "enum"
        and not enum_value.__str__.__module__.startswith("shibokensupport")
    ):
        # check if function was overloaded
        name = str(enum_value)
    else:
        name = enum_value.name.replace("_", " ")
    return name


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
        super().addItems(list(map(_get_name, self._enum_class.__members__.values())))

    def enumClass(self) -> Optional[EnumMeta]:
        """return current Enum class."""
        return self._enum_class

    def isOptional(self) -> bool:
        """return if current enum is with optional annotation."""
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
                else:
                    return list(self._enum_class.__members__.values())[
                        self.currentIndex() - 1
                    ]
            return list(self._enum_class.__members__.values())[self.currentIndex()]
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
