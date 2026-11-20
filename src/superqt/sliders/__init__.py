import warnings
from typing import Any

from ._generic_slider import MONTEREY_SLIDER_STYLES_FIX as _MONTEREY_STYLES
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


def __getattr__(name: str) -> Any:
    if name == "MONTEREY_SLIDER_STYLES_FIX":
        warnings.warn(
            "MONTEREY_SLIDER_STYLES_FIX is deprecated and will be removed in a "
            "future version. Call `applyMacStylePatch()` on the slider instead, "
            "or set the `USE_MAC_SLIDER_PATCH=1` environment variable.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _MONTEREY_STYLES
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
