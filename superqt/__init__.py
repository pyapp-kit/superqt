"""superqt is a collection of QtWidgets for python."""
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._eliding_label import QElidingLabel
from .combobox import QEnumComboBox
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
from .utils import QMessageHandler

__all__ = [
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QElidingLabel",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QMessageHandler",
    "QRangeSlider",
    "QEnumComboBox",
]
