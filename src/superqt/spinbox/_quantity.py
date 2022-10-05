from typing import TYPE_CHECKING, Optional, Union

try:
    from pint import Quantity, Unit, UnitRegistry
    from pint.util import UnitsContainer
except ImportError as e:
    raise ImportError(
        "pint is required to use QQuantity.  Install it with `pip install pint`"
    ) from e

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QSizePolicy, QWidget

from ..utils import signals_blocked

if TYPE_CHECKING:
    from decimal import Decimal


Number = Union[int, float, "Decimal"]
UREG = UnitRegistry()
NULL_OPTION = "-----"
SI_BASES = {
    "[length]": "meter",
    "[time]": "second",
    "[current]": "ampere",
    "[luminosity]": "candela",
    "[mass]": "gram",
    "[substance]": "mole",
    "[temperature]": "kelvin",
}
DEFAULT_OPTIONS = {
    "[length]": ["km", "m", "mm", "µm"],
    "[time]": ["day", "hour", "min", "sec", "ms"],
    "[current]": ["A", "mA", "µA"],
    "[luminosity]": ["kcd", "cd", "mcd"],
    "[mass]": ["kg", "g", "mg", "µg"],
    "[substance]": ["mol", "mmol", "µmol"],
    "[temperature]": ["°C", "°F", "°K"],
    "radian": ["rad", "deg"],
}


class QQuantity(QWidget):
    """A combination QDoubleSpinBox and QComboBox for entering quantities.

    For this widget, `value()` returns a `pint.Quantity` object, while `setValue()`
    accepts either a number, `pint.Quantity`, a string that can be parsed by `pint`.
    """

    valueChanged = Signal(Quantity)
    unitsChanged = Signal(Unit)
    dimensionalityChanged = Signal(UnitsContainer)

    def __init__(
        self,
        value: Union[str, Quantity, Number],
        units: Union[UnitsContainer, str, Quantity] = None,
        ureg: Optional[UnitRegistry] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        if ureg is None:
            ureg = value._REGISTRY if isinstance(value, Quantity) else UREG
        else:
            assert isinstance(ureg, UnitRegistry)

        self._ureg = ureg
        self._value: Quantity = self._ureg.Quantity(value, units=units)

        # whether to preserve quantity equality when changing units or magnitude
        self._preserve_quantity: bool = False
        self._abbreviate_units: bool = True  # TODO: implement

        self._mag_spinbox = QDoubleSpinBox()
        self._mag_spinbox.setDecimals(3)
        self._mag_spinbox.setRange(-9999999999999, 99999999999999)
        self._mag_spinbox.setValue(float(self._value.magnitude))
        self._mag_spinbox.valueChanged.connect(self.setMagnitude)

        self._units_combo = QComboBox()
        self._units_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._units_combo.currentTextChanged.connect(self.setUnits)
        self._update_units_combo_choices()

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self._mag_spinbox)
        self.layout().addWidget(self._units_combo)
        self.layout().setContentsMargins(6, 0, 0, 0)

    def unitRegistry(self) -> UnitRegistry:
        return self._ureg

    def _update_units_combo_choices(self):
        if self._value.dimensionless:
            with signals_blocked(self._units_combo):
                self._units_combo.clear()
                self._units_combo.addItem(NULL_OPTION)
                self._units_combo.addItems(
                    [self._format_units(x) for x in SI_BASES.values()]
                )
                self._units_combo.setCurrentText(NULL_OPTION)
            return

        units = self._value.units
        dims, exp = next(iter(units.dimensionality.items()))
        if exp != 1:
            raise NotImplementedError("Inverse units not yet implemented")
        options = [
            self._format_units(self._ureg.Unit(u))
            for u in DEFAULT_OPTIONS.get(dims, [])
        ]
        current = self._format_units(units)
        with signals_blocked(self._units_combo):
            self._units_combo.clear()
            self._units_combo.addItems(options)
            if self._units_combo.findText(current) == -1:
                self._units_combo.addItem(current)

        self._units_combo.setCurrentText(current)

    def value(self) -> Quantity:
        return self._value

    def magnitude(self) -> Union[float, int]:
        return self._value.magnitude

    def units(self) -> Unit:
        return self._value.units

    def dimensionality(self) -> UnitsContainer:
        return self._value.dimensionality

    def setDecimals(self, decimals: int) -> None:
        self._mag_spinbox.setDecimals(decimals)
        if self._value is not None:
            self._mag_spinbox.setValue(self._value.magnitude)

    def setValue(self, quantity: Union[str, Quantity, Number]) -> None:
        new_val = self._ureg.Quantity(quantity)

        mag_change = new_val.magnitude != self._value.magnitude
        units_change = new_val.units != self._value.units
        dims_changed = new_val.dimensionality != self._value.dimensionality

        self._value = new_val

        if mag_change:
            with signals_blocked(self._mag_spinbox):
                self._mag_spinbox.setValue(float(self._value.magnitude))

        if units_change:
            with signals_blocked(self._units_combo):
                self._units_combo.setCurrentText(self._format_units(self._value.units))
            self.unitsChanged.emit(self._value.units)

        if dims_changed:
            self._update_units_combo_choices()
            self.dimensionalityChanged.emit(self._value.dimensionality)

        if mag_change or units_change:
            self.valueChanged.emit(self._value)

    def setMagnitude(self, magnitude: Number) -> None:
        self.setValue(self._ureg.Quantity(magnitude, self._value.units))

    def setUnits(self, units: Union[str, Unit, Quantity]) -> None:
        if units is None:
            new_val = self._ureg.Quantity(self._value.magnitude)
        elif self.isDimensionless():
            new_val = self._ureg.Quantity(self._value.magnitude, units)
        else:
            new_val = self._value.to(units)
        self.setValue(new_val)

    def isDimensionless(self) -> bool:
        return self._value.dimensionless

    def magnitudeSpinBox(self) -> QDoubleSpinBox:
        return self._mag_spinbox

    def unitsComboBox(self) -> QComboBox:
        return self._units_combo

    def _format_units(self, u: Union[Unit, str]) -> str:
        if isinstance(u, str):
            return u
        return f"{u:~}" if self._abbreviate_units else f"{u:}"
