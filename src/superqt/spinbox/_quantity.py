from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional, Union

try:
    from pint import DimensionalityError, Quantity, Unit, UnitRegistry
except ImportError:
    raise ImportError(
        "pint is required to use QQuantity.  Install it with `pip install pint`"
    )

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout, QWidget

if TYPE_CHECKING:
    from decimal import Decimal


ureg = UnitRegistry()
Q_ = ureg.Quantity
U_ = ureg.Unit
dims = ureg._dimensions
Number = Union[int, float, "Decimal"]


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
    "[temperature]": ["°C", "°F"]  # '°K'?
    # "radian": ['rad', 'deg'],
}


class QQuantity(QWidget):
    valueChanged = Signal(Quantity)
    unitsChanged = Signal(str)
    magnitudeChanged = Signal(float)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._value: Optional[Quantity] = None
        self._abbreviate_units = True

        self._magnitude_wdg = QDoubleSpinBox()
        self._magnitude_wdg.setRange(-999999999999999999999, 9999999999999999999)
        self._magnitude_wdg.valueChanged.connect(self._on_mag_changed)
        self._units_wdg = QComboBox()
        self._units_wdg.currentTextChanged.connect(self._on_units_changed)
        self._compact_check = QCheckBox()
        self._strict_dims: bool = True

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self._magnitude_wdg)
        self.layout().addWidget(self._units_wdg)
        self.layout().addWidget(self._compact_check)
        self.layout().setContentsMargins(6, 0, 0, 0)

    def _on_mag_changed(self, mag: Number):
        val = Q_(mag, self.units())
        if self._compact_check.isChecked():
            self.setValue(val.to_compact())
        else:
            self._value = val

    def _on_units_changed(self, units: str) -> None:
        self.setUnits(units)

    def magnitude(self) -> Number:
        return self._value.magnitude if self._value else 0

    def setMagnitude(self, mag: Number) -> None:
        val = Q_(mag, self.units())
        if self._compact_check.isChecked():
            self.setValue(val.to_compact())
        if val.magnitude != self._magnitude_wdg.value():
            self._magnitude_wdg.setValue(val.magnitude)

    def decimals(self) -> int:
        return self._magnitude_wdg.decimals()

    def setDecimals(self, decimals: int) -> None:
        self._magnitude_wdg.setDecimals(decimals)
        if self._value is not None:
            self._magnitude_wdg.setValue(self._value.magnitude)

    def units(self) -> str:
        return str(self._value.units) if self._value else ""

    def setUnits(self, units: Union[str, Quantity, Unit, None]) -> None:
        if isinstance(units, Quantity):
            _units: Unit = units.units
        elif units is None:
            _units = Unit("")
        elif isinstance(units, str):
            _units = Unit(units)
        else:
            _units = units
        if not isinstance(_units, Unit):
            raise TypeError(f"{_units} is not a Unit type")

        if self._value is None:
            self._value = Q_(1, _units)
            self._populate_units(_units)
            self.setMagnitude(1)
            return
        else:
            try:
                self._value = self._value.to(_units)
                with self._signals_blocked():
                    self._magnitude_wdg.setValue(self._value.magnitude)
                    self._units_wdg.setCurrentText(str(self._value.units))
            except DimensionalityError:
                if self._strict_dims:
                    raise
                self._populate_units(units)

    def _maybe_add_unit(self, unit):
        t = self._format_units(unit)
        if self._units_wdg.findText(t) == -1:
            self._units_wdg.addItem(t)

    def _populate_units(self, units: Unit):
        dims, exp = next(iter(units.dimensionality.items()))
        if exp != 1:
            raise NotImplementedError("Inverse units not yet implemented")
        options = [self._format_units(U_(u)) for u in DEFAULT_OPTIONS.get(dims, [])]
        with self._signals_blocked():
            self._units_wdg.addItems(options)
            self._maybe_add_unit(units)
            self._units_wdg.setCurrentText(self._format_units(units))

    @contextmanager
    def _signals_blocked(self):
        self._magnitude_wdg.blockSignals(True)
        self._units_wdg.blockSignals(True)
        try:
            yield
        finally:
            self._magnitude_wdg.blockSignals(False)
            self._units_wdg.blockSignals(False)

    def _format_units(self, u: Unit) -> str:
        if self._abbreviate_units:
            return f"{u:~}"
        return f"{u:}"

    def value(self) -> Quantity:
        return self._value

    def setValue(self, quantity: Union[str, Quantity, Number]) -> None:
        with self._signals_blocked():
            self.clear()
        val = Q_(quantity)
        self.setUnits(val.units)
        self._magnitude_wdg.setValue(float(val.magnitude))
        self._value = val

    def strictDimensionality(self) -> bool:
        return self._strict_dims

    def setStrictDimensionality(self, strict: bool) -> None:
        self._strict_dims = bool(strict)

    def magnitudeSpinBox(self) -> QDoubleSpinBox:
        return self._magnitude_wdg

    def unitsComboBox(self) -> QComboBox:
        return self._units_wdg

    def clear(self) -> None:
        self._value = None
        self._units_wdg.clear()
