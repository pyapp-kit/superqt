try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._labeled import QLabeledRangeSlider, QLabeledSlider
from ._qrangeslider import QRangeSlider

__all__ = ["QRangeSlider", "QLabeledRangeSlider", "QLabeledSlider"]
