from typing import Optional, Type, TypeVar, Union
from enum import Enum

from ..qtcompat.QtWidgets import QComboBox
from ..qtcompat.QtCore import Signal, PYQT5

EnumType = TypeVar("EnumType", bound=Enum)
enum_type = Enum if PYQT5 else object

def _get_name(enum_value: Enum):
    """Create human readable name if user does not provide own implementation of __str__"""
    if enum_value.__str__.__module__ != "enum":
        # check if function was overloaded
        name = str(enum_value)
    else:
        name = enum_value.name.replace("_", " ")
    return name


class EnumComboBox(QComboBox):
    """
    ComboBox presenting options from a python Enum.

    If the Enum class does not implement `__str__` then a human readable name
    is created from the name of the enum member, replacing underscores with spaces.
    """
    currentEnumChanged = Signal(enum_type)

    def __init__(self, parent=None, enum_class:Optional[Type[EnumType]] = None):
        super().__init__(parent)
        self._enum_class = None
        if enum_class is not None:
            self.setEnumClass(enum_class)
        self.currentIndexChanged.connect(self._emit_signal)

    def setEnumClass(self, enum: Type[EnumType]):
        """
        Set enum class from which members value should be selected
        """
        self.clear()
        self._enum_class = enum
        super().addItems(list(map(_get_name, enum.__members__.values())))

    def enumClass(self) -> Optional[Type[EnumType]]:
        """return current Enum class"""
        return self._enum_class

    def clear(self):
        self._enum_class = None
        super().clear()

    def currentEnum(self) -> Optional[EnumType]:
        """current value as Enum member"""
        if self._enum_class is not None:
            return list(self._enum_class.__members__.values())[self.currentIndex()]
        return None

    def setCurrentEnum(self, value: EnumType) -> None:
        """Set value with Enum."""
        if not isinstance(value, Enum):
            raise TypeError(f'setValue(self, Enum): argument 1 has unexpected type {type(value).__name__!r}')
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
