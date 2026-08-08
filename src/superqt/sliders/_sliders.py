from qtpy.QtCore import Signal

from ._generic_range_slider import _GenericRangeSlider
from ._generic_slider import _GenericSlider


class _IntMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singleStep = 1

    def _type_cast(self, value) -> int:
        return round(value)


class _FloatMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singleStep = 0.01
        self._pageStep = 0.1

    def _type_cast(self, value) -> float:
        return float(value)


class QDoubleSlider(_FloatMixin, _GenericSlider):
    pass


class QIntSlider(_IntMixin, _GenericSlider):
    # mostly just an example... use QSlider instead.
    valueChanged = Signal(int)


class QRangeSlider(_IntMixin, _GenericRangeSlider):
    def _rename_signals(self) -> None:
        super()._rename_signals()
        # QSlider.rangeChanged is Signal(int, int) and cannot carry values
        # outside the signed 32-bit range. Rebind to frangeChanged so large
        # integer ranges (e.g. 0..10**11 in examples/labeled_sliders.py) work.
        # Mirrors QDoubleRangeSlider. See #308.
        self.rangeChanged = self.frangeChanged


class QDoubleRangeSlider(_FloatMixin, QRangeSlider):
    def _rename_signals(self) -> None:
        super()._rename_signals()
        self.rangeChanged = self.frangeChanged


# QRangeSlider.__doc__ += "\n" + textwrap.indent(QSlider.__doc__, "    ")
