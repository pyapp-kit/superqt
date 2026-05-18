import pytest
from pint import Quantity

from superqt import QQuantity


def test_qquantity(qtbot):
    w = QQuantity(1, "m")
    qtbot.addWidget(w)

    assert w.value() == 1 * w.unitRegistry().meter
    assert w.magnitude() == 1
    assert w.units() == w.unitRegistry().meter
    assert w.text() == "1 meter"
    w.setUnits("cm")
    assert w.value() == 100 * w.unitRegistry().centimeter
    assert w.magnitude() == 100
    assert w.units() == w.unitRegistry().centimeter
    assert w.text() == "100.0 centimeter"
    w.setMagnitude(10)
    assert w.value() == 10 * w.unitRegistry().centimeter
    assert w.magnitude() == 10
    assert w.units() == w.unitRegistry().centimeter
    assert w.text() == "10 centimeter"
    w.setValue(1 * w.unitRegistry().meter)
    assert w.value() == 1 * w.unitRegistry().meter
    assert w.magnitude() == 1
    assert w.units() == w.unitRegistry().meter
    assert w.text() == "1 meter"

    w.setUnits(None)
    assert w.isDimensionless()
    assert w.unitsComboBox().currentText() == "-----"
    assert w.magnitude() == 1


def test_qquantity_exponents(qtbot):
    w = QQuantity(1, "m^2")
    qtbot.addWidget(w)

    assert w.value() == 1 * w.unitRegistry().meter ** 2
    assert w.magnitude() == 1
    assert w.units() == w.unitRegistry().meter ** 2
    assert w.text() == "1 meter ** 2"
    w.setUnits("cm^2")
    assert w.value() == 10000 * w.unitRegistry().centimeter ** 2
    assert w.magnitude() == 10000
    assert w.units() == w.unitRegistry().centimeter ** 2
    assert w.text() == "10000.0 centimeter ** 2"


def test_qquantity_non_simple_units(qtbot):
    with pytest.raises(NotImplementedError):
        qtbot.addWidget(QQuantity(1, "m/s"))

    with pytest.raises(NotImplementedError):
        qtbot.addWidget(QQuantity(1, "N"))


def test_change_qquantity_value(qtbot):
    w = QQuantity()
    qtbot.addWidget(w)
    assert w.value() == Quantity(0)
    w.setValue(Quantity("1 meter"))
    assert w.value() == Quantity("1 meter")
