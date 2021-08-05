"""superqt is a collection of QtWidgets for python."""
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._label import QElidingLabel
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

__all__ = [
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QElidingLabel",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QRangeSlider",
]
