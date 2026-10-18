import pytest
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget

from superqt import QLabeledMappedSlider


def test_constructor_overloads(qtbot):
    parent = QWidget()
    qtbot.addWidget(parent)
    assert QLabeledMappedSlider(parent).parent() is parent
    slider = QLabeledMappedSlider(Qt.Orientation.Vertical, parent)
    assert slider.orientation() == Qt.Orientation.Vertical


def test_log_mapping(qtbot):
    slider = QLabeledMappedSlider()
    qtbot.addWidget(slider)
    slider.setRange(1, 100)

    slider._slider.setValue(0.5)
    assert slider.value() == pytest.approx(10)

    slider.setValue(100)
    slider.setValue(10)
    assert slider._slider.value() == pytest.approx(0.5)


def test_power_mapping(qtbot):
    slider = QLabeledMappedSlider()
    qtbot.addWidget(slider)
    slider.setMapping("power")
    slider.setExponent(1)
    slider.setRange(0, 1000)

    slider._slider.setValue(0.5)
    assert slider.value() == pytest.approx(500)

    slider.setExponent(2)
    slider._slider.setValue(0.5)
    assert slider.value() == pytest.approx(250)

    slider.setValue(1000)
    slider.setValue(250)
    assert slider._slider.value() == pytest.approx(0.5)


def test_set_value_is_exact_and_clamped(qtbot):
    slider = QLabeledMappedSlider()
    qtbot.addWidget(slider)
    slider.setMapping("power")
    slider.setRange(0, 0.5)
    values = []
    slider.valueChanged.connect(values.append)

    slider.setValue(0.005)
    assert slider.value() == 0.005

    slider.setValue(0.005)
    assert values == [0.005]

    slider.setValue(2)
    assert slider.value() == 0.5


def test_typing_in_label(qtbot):
    slider = QLabeledMappedSlider()
    qtbot.addWidget(slider)
    slider.setMapping("power")
    slider.setRange(0, 1000)

    slider._label.setText("250")
    slider._label.editingFinished.emit()
    assert slider.value() == 250
    assert slider._slider.value() == pytest.approx(0.25 ** (1 / 3))


def test_bad_input_is_refused(qtbot):
    slider = QLabeledMappedSlider()
    qtbot.addWidget(slider)

    with pytest.raises(ValueError):
        slider.setRange(0, 1)
    with pytest.raises(ValueError):
        slider.setMapping("sin")
    with pytest.raises(ValueError):
        slider.setExponent(0)
