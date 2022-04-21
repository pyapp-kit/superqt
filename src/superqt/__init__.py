"""superqt is a collection of QtWidgets for python."""
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


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
    "QDoubleSlider",
    "QElidingLabel",
    "QEnumComboBox",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QMessageHandler",
    "QSearchableComboBox",
    "QSearchableListWidget",
    "QRangeSlider",
    "QCollapsible",
]
