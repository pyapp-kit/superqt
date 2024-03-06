"""superqt is a collection of Qt components for python."""

from importlib.metadata import PackageNotFoundError, version
from typing import Any

try:
    __version__ = version("superqt")
except PackageNotFoundError:
    __version__ = "unknown"

from .collapsible import QCollapsible
from .combobox import (
    QColorComboBox,
    QColormapComboBox,
    QEnumComboBox,
    QSearchableComboBox,
)
from .elidable import QElidingLabel, QElidingLineEdit
from .iconify import QIconifyIcon
from .selection import QSearchableListWidget, QSearchableTreeWidget
from .sliders import (
    QDoubleRangeSlider,
    QDoubleSlider,
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
    QRangeSlider,
)
from .spinbox import QLargeIntSpinBox
from .spinbox._quantity import QQuantity
from .utils import QMessageHandler, ensure_main_thread, ensure_object_thread

__all__ = [
    "ensure_main_thread",
    "ensure_object_thread",
    "QCollapsible",
    "QColorComboBox",
    "QColormapComboBox",
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QElidingLabel",
    "QElidingLineEdit",
    "QEnumComboBox",
    "QLabeledDoubleRangeSlider",
    "QIconifyIcon",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QMessageHandler",
    "QQuantity",
    "QRangeSlider",
    "QSearchableComboBox",
    "QSearchableListWidget",
    "QSearchableTreeWidget",
]


def __getattr__(name: str) -> Any:
    if name == "QQuantity":
        from .spinbox._quantity import QQuantity

        return QQuantity
    if name == "QColormapComboBox":
        from .cmap import QColormapComboBox

        return QColormapComboBox
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
