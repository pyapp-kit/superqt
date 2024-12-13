"""superqt is a collection of Qt components for python."""

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

try:
    __version__ = version("superqt")
except PackageNotFoundError:
    __version__ = "unknown"

from .collapsible import QCollapsible
from .combobox import QColorComboBox, QEnumComboBox, QSearchableComboBox
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
from .utils import QMessageHandler, ensure_main_thread, ensure_object_thread

__all__ = [
    "QCollapsible",
    "QColorComboBox",
    "QColormapComboBox",
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QElidingLabel",
    "QElidingLineEdit",
    "QEnumComboBox",
    "QIconifyIcon",
    "QLabeledDoubleRangeSlider",
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
    "ensure_main_thread",
    "ensure_object_thread",
]

if TYPE_CHECKING:
    from .combobox import QColormapComboBox  # noqa: TC004
    from .spinbox._quantity import QQuantity  # noqa: TC004


def __getattr__(name: str) -> Any:
    if name == "QQuantity":
        from .spinbox._quantity import QQuantity

        return QQuantity
    if name == "QColormapComboBox":
        from .cmap import QColormapComboBox

        return QColormapComboBox
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
