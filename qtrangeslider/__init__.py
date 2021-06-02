try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._labeled import (
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
)
from ._sliders import QDoubleRangeSlider, QDoubleSlider, QRangeSlider

__all__ = [
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QRangeSlider",
]
