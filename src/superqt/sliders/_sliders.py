from qtpy.QtCore import Signal

from ._generic_range_slider import _GenericRangeSlider
from ._generic_slider import _GenericSlider


class _IntMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._singleStep = 1

    def _type_cast(self, value) -> int:
        return int(round(value))


class _FloatMixin:
    _fvalueChanged = Signal(float)
    _fsliderMoved = Signal(float)
    _frangeChanged = Signal(float, float)

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
    pass


class QDoubleRangeSlider(_FloatMixin, QRangeSlider):
    pass


# QRangeSlider.__doc__ += "\n" + textwrap.indent(QSlider.__doc__, "    ")
