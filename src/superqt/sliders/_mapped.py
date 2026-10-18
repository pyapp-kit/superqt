from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Literal

from qtpy.QtCore import Qt

from ._labeled import QLabeledDoubleSlider

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

# A string representing the slider position to value transfer function.
# Currently only "log" and "power" are supported.
Mapping = Literal["log", "power"]


def _check_mapping(mapping: str) -> None:
    if mapping not in ("log", "power"):
        raise ValueError(f"mapping must be 'log' or 'power', not {mapping!r}")


def _check_exponent(exponent: float) -> None:
    if exponent <= 0:
        raise ValueError("exponent must be greater than 0")


class QLabeledMappedSlider(QLabeledDoubleSlider):
    """A labeled float slider whose value follows a non-linear curve.

    The handle moves evenly along the slider, while the value it represents
    follows ``mapping``. Below, ``p`` is the handle position, from 0 at the
    left to 1 at the right.

    ``"log"``: ``value = minimum * (maximum / minimum) ** p``

    Each decade gets the same room on the slider. With a range of 1 to 100,
    the middle of the slider is 10. The minimum must be greater than 0.

    ``"power"``: ``value = minimum + (maximum - minimum) * p ** exponent``

    With a range of 0 to 1000, the middle of the slider is 500 for
    ``exponent=1`` (a normal linear slider) and 250 for ``exponent=2``.
    Larger exponents give finer control near the minimum, which can be 0.
    """

    # Set here, not in __init__: the parent's __init__ already calls our methods,
    # and missing attributes would be looked up on the inner slider instead.
    _mapping: Mapping = "log"
    _exponent: float = 3.0
    _mapped_minimum: float = 0.01
    _mapped_maximum: float = 1.0
    _mapped_value: float = 0.01

    def __init__(
        self,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        parent: QWidget | None = None,
        mapping: Mapping = "log",
        exponent: float = 3.0,
    ) -> None:
        super().__init__(orientation, parent)
        self._slider.setRange(0, 1)
        self._slider.setSingleStep(0.01)
        self._slider.setPageStep(0.1)
        _check_mapping(mapping)
        _check_exponent(exponent)
        self._mapping = mapping
        self._exponent = float(exponent)
        if mapping == "log":
            self.setRange(0.01, 1.0)
        else:
            self.setRange(0.0, 1.0)

    def mapping(self) -> Mapping:
        return self._mapping

    def setMapping(self, mapping: Mapping) -> None:
        _check_mapping(mapping)
        if mapping == "log" and self._mapped_minimum <= 0:
            raise ValueError("with 'log' mapping the minimum must be greater than 0")
        self._mapping = mapping
        self._move_handle_to_value()

    def exponent(self) -> float:
        return self._exponent

    def setExponent(self, exponent: float) -> None:
        _check_exponent(exponent)
        self._exponent = float(exponent)
        self._move_handle_to_value()

    def minimum(self) -> float:
        return self._mapped_minimum

    def maximum(self) -> float:
        return self._mapped_maximum

    def setMinimum(self, minimum: float) -> None:
        self.setRange(minimum, max(minimum, self._mapped_maximum))

    def setMaximum(self, maximum: float) -> None:
        self.setRange(min(self._mapped_minimum, maximum), maximum)

    def setRange(self, minimum: float, maximum: float) -> None:
        if self._mapping == "log" and minimum <= 0:
            raise ValueError("with 'log' mapping the minimum must be greater than 0")
        self._mapped_minimum = float(minimum)
        self._mapped_maximum = float(max(minimum, maximum))
        self._label.setRange(self._mapped_minimum, self._mapped_maximum)
        old_value = self._mapped_value
        self._mapped_value = self._clamp(old_value)
        self._move_handle_to_value()
        self.rangeChanged.emit(self._mapped_minimum, self._mapped_maximum)
        if self._mapped_value != old_value:
            self.valueChanged.emit(self._mapped_value)

    def value(self) -> float:
        return self._mapped_value

    def setValue(self, value: float) -> None:
        value = self._clamp(value)
        if value == self._mapped_value:
            return
        self._mapped_value = value
        self._move_handle_to_value()
        self.valueChanged.emit(value)

    def _clamp(self, value: float) -> float:
        return min(max(float(value), self._mapped_minimum), self._mapped_maximum)

    def _to_value(self, position: float) -> float:
        lo, hi = self._mapped_minimum, self._mapped_maximum
        if self._mapping == "log":
            return lo * (hi / lo) ** position
        return lo + (hi - lo) * position**self._exponent

    def _to_position(self, value: float) -> float:
        lo, hi = self._mapped_minimum, self._mapped_maximum
        if hi == lo:
            return 0.0
        if self._mapping == "log":
            return math.log(value / lo) / math.log(hi / lo)
        return ((value - lo) / (hi - lo)) ** (1 / self._exponent)

    def _move_handle_to_value(self) -> None:
        self._label.setValue(self._mapped_value)
        # Move the handle without triggering _on_slider_value_changed, which
        # would replace the exact value with one recomputed from the position.
        blocked = self._slider.blockSignals(True)
        self._slider.setValue(self._to_position(self._mapped_value))
        self._slider.blockSignals(blocked)
        self._slider.update()

    def _on_slider_value_changed(self, position: Any) -> None:
        self._mapped_value = self._to_value(position)
        self._label.setValue(self._mapped_value)
        self.valueChanged.emit(self._mapped_value)

    def _on_slider_range_changed(self, min_: float, max_: float) -> None:
        # The inner slider's range is always 0 to 1; setRange emits the real one.
        pass

    def _setValue(self, value: float) -> None:
        self.setValue(value)
