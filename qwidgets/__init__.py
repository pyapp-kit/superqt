"""qwidgets is a collection of QtWidgets for python."""
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from .sliders import (
    QDoubleRangeSlider,
    QDoubleSlider,
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
    QRangeSlider,
)

__all__ = [
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QRangeSlider",
]
