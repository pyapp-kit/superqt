import math
from typing import Tuple

from ._hooked import _HookedSlider
from ._qrangeslider import QRangeSlider
from .qtcompat.QtCore import Signal


class QDoubleSlider(_HookedSlider):

    valueChanged = Signal(float)
    rangeChanged = Signal(float, float)
    sliderMoved = Signal(float)
    _multiplier = 1

    def __init__(self, *args):
        super().__init__(*args)
        self._multiplier = 10 ** 2
        self.setMinimum(0)
        self.setMaximum(99)
        self.setSingleStep(1)
        self.setPageStep(10)
        super().sliderMoved.connect(
            lambda e: self.sliderMoved.emit(self._post_get_hook(e))
        )

    def decimals(self) -> int:
        """This property holds the precision of the slider, in decimals."""
        return int(math.log10(self._multiplier))

    def setDecimals(self, prec: int):
        """This property holds the precision of the slider, in decimals

        Sets how many decimals the slider uses for displaying and interpreting doubles.
        """
        previous = self._multiplier
        self._multiplier = 10 ** int(prec)
        ratio = self._multiplier / previous

        if ratio != 1:
            self.blockSignals(True)
            try:
                newmin = self.minimum() * ratio
                newmax = self.maximum() * ratio
                newval = self._scale_value(ratio)
                newstep = self.singleStep() * ratio
                newpage = self.pageStep() * ratio
                self.setRange(newmin, newmax)
                self.setValue(newval)
                self.setSingleStep(newstep)
                self.setPageStep(newpage)
            except OverflowError as err:
                self._multiplier = previous
                raise OverflowError(
                    f"Cannot use {prec} decimals with a range of {newmin}-"
                    f"{newmax}. If you need this feature, please open a feature"
                    " request at github."
                ) from err
            self.blockSignals(False)

    def _scale_value(self, p):
        # for subclasses
        return self.value() * p

    def _post_get_hook(self, value: int) -> float:
        return value / self._multiplier

    def _pre_set_hook(self, value: float) -> int:
        return int(value * self._multiplier)

    def sliderChange(self, change) -> None:
        if change == self.SliderValueChange:
            self.valueChanged.emit(self.value())
        if change == self.SliderRangeChange:
            self.rangeChanged.emit(self.minimum(), self.maximum())
        return super().sliderChange(self.SliderChange(change))


class QDoubleRangeSlider(QRangeSlider, QDoubleSlider):
    rangeChanged = Signal(float, float)

    def value(self) -> Tuple[float, ...]:
        """Get current value of the widget as a tuple of integers."""
        return tuple(float(i) for i in self._value)

    def _min_max_bound(self, val: int) -> float:
        return round(super()._min_max_bound(val), self.decimals())

    def _scale_value(self, p):
        # This function is called during setDecimals...
        # but because QRangeSlider has a private nonQt `_value`
        # we don't actually need to scale
        return self._value

    def setDecimals(self, prec: int):
        return super().setDecimals(prec)
