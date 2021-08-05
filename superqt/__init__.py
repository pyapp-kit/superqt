"""superqt is a collection of Qt components for python."""
from typing import TYPE_CHECKING

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

if TYPE_CHECKING:
    try:
        from .compound._quantity import QQuantity
    except ImportError:
        pass

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
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QQuantity",
    "QRangeSlider",
]


def __getattr__(name):
    if name == "QQuantity":
        from .compound._quantity import QQuantity

        return QQuantity
    raise ImportError(f"cannot import name {name!r} from {__name__!r}")
