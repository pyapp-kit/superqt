try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._float_slider import QDoubleRangeSlider, QDoubleSlider
from ._labeled import (
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
)
from ._qrangeslider import QRangeSlider

__all__ = [
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QRangeSlider",
]
