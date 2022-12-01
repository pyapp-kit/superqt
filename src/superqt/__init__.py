"""superqt is a collection of Qt components for python."""
from typing import TYPE_CHECKING, Any

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

if TYPE_CHECKING:
    from .spinbox._quantity import QQuantity

from ._eliding_label import QElidingLabel
from .collapsible import QCollapsible
from .combobox import QEnumComboBox, QSearchableComboBox
from .selection import QSearchableListWidget
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
    "ensure_main_thread",
    "ensure_object_thread",
    "QDoubleRangeSlider",
    "QCollapsible",
    "QDoubleSlider",
    "QElidingLabel",
    "QEnumComboBox",
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
]


def __getattr__(name: str) -> Any:
    if name == "QQuantity":
        from .spinbox._quantity import QQuantity

        return QQuantity
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
