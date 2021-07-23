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
        self.enum = enum
        if enum is not None:
            self.setEnum(enum)
        self.currentIndexChanged.connect(self._emit_signal)

    def setEnum(self, enum: Type[EnumType]):
        """
        Set enum class from which members value should be selected
        """
        self.clear()
        self.enum = enum
        super().addItems(list(map(_get_name, enum.__members__.values())))

    def clear(self):
        self.enum = None
        super().clear()

    def currentValue(self) -> EnumType:
        """current value as Enum member"""
        if self.enum is None:
            raise RuntimeError("Enum value is None")
        return list(self.enum.__members__.values())[self.currentIndex()]

    def setValue(self, value: Union[EnumType, int]):
        """Set value with Enum or int"""
        if not isinstance(value, (Enum, int)):
            return
        if isinstance(value, Enum):
            self.setCurrentText(_get_name(value))
        else:
            self.setCurrentIndex(value)

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
