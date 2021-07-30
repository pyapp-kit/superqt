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
    This is implementation of variant of EnumComboBox for select enum value.
    If enum class does not provide own __str__ implementation then human readable name is provide using name of item
    replacing underscores with spaces.
    """
    currentValueChanged = Signal(enum_type)

    def __init__(self, parent=None, enum:Optional[Type[EnumType]] = None):
        super().__init__(parent)
        self._enum = enum
        if enum is not None:
            self.setEnum(enum)
        self.currentIndexChanged.connect(self._emit_signal)

    def setEnum(self, enum: Type[EnumType]):
        """
        Set enum class from which members value should be selected
        """
        self.clear()
        self._enum = enum
        super().addItems(list(map(_get_name, enum.__members__.values())))

    def enum(self) -> Optional[Type[EnumType]]:
        return self._enum

    def clear(self):
        self._enum = None
        super().clear()

    def currentValue(self) -> EnumType:
        """current value as Enum member"""
        if self._enum is None:
            raise RuntimeError("Enum value is None")
        return list(self._enum.__members__.values())[self.currentIndex()]

    def setValue(self, value: EnumType) -> None:
        """Set value with Enum."""
        if not isinstance(value, Enum):
            raise TypeError(f'setValue(self, Enum): argument 1 has unexpected type {type(value).__name__!r}')
        self.setCurrentText(_get_name(value))

    def _emit_signal(self):
        try:
            self.currentValueChanged.emit(self.currentValue())
        except RuntimeError:
            pass

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
