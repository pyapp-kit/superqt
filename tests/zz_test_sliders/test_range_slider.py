import math
from collections.abc import Iterable
from itertools import product
from typing import Any
from unittest.mock import Mock

import pytest
from qtpy.QtCore import QEvent, QPoint, QPointF, Qt
from qtpy.QtWidgets import QStyle, QStyleOptionSlider

from superqt import QDoubleRangeSlider, QLabeledRangeSlider, QRangeSlider

from ._testutil import (
    _hover_event,
    _linspace,
    _mouse_event,
    _wheel_event,
    skip_on_linux_qt6,
)

ALL_SLIDER_COMBOS = list(
    product(
        [QDoubleRangeSlider, QRangeSlider, QLabeledRangeSlider],
        [Qt.Orientation.Horizontal, Qt.Orientation.Vertical],
    )
)
FLOAT_SLIDERS = [c for c in ALL_SLIDER_COMBOS if c[0] == QDoubleRangeSlider]


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_slider_init(qtbot, cls, orientation):
    slider = cls(orientation)
    assert slider.value() == (20, 80)
    assert slider.minimum() == 0
    assert slider.maximum() == 99
    slider.show()
    qtbot.addWidget(slider)


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_change_floatslider_range(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    with qtbot.waitSignals([sld.rangeChanged, sld.valueChanged]):
        sld.setMinimum(30)

    assert sld.value()[0] == 30 == sld.minimum()
    assert sld.maximum() == 99

    with qtbot.waitSignal(sld.rangeChanged):
        sld.setMaximum(70)
    assert sld.value()[0] == 30 == sld.minimum()
    assert sld.value()[1] == 70 == sld.maximum()

    with qtbot.waitSignals([sld.rangeChanged, sld.valueChanged]):
        sld.setRange(40, 60)
    assert sld.value()[0] == 40 == sld.minimum()
    assert sld.maximum() == 60

    with qtbot.waitSignal(sld.valueChanged):
        sld.setValue([40, 50])
    assert sld.value()[0] == 40 == sld.minimum()
    assert sld.value()[1] == 50

    with qtbot.waitSignals([sld.rangeChanged, sld.valueChanged]):
        sld.setMaximum(45)
    assert sld.value()[0] == 40 == sld.minimum()
    assert sld.value()[1] == 45 == sld.maximum()


@pytest.mark.parametrize("cls, orientation", FLOAT_SLIDERS)
def test_float_values(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    with qtbot.waitSignal(sld.rangeChanged):
        sld.setRange(0.1, 0.9)
    assert sld.minimum() == 0.1
    assert sld.maximum() == 0.9

    with qtbot.waitSignal(sld.valueChanged):
        sld.setValue([0.4, 0.6])
    assert sld.value() == (0.4, 0.6)

    with qtbot.waitSignal(sld.valueChanged):
        sld.setValue([0, 1.9])
    assert sld.value()[0] == 0.1 == sld.minimum()
    assert sld.value()[1] == 0.9 == sld.maximum()


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_position(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    sld.setSliderPosition([10, 80])
    assert sld.sliderPosition() == (10, 80)


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_steps(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    sld.setSingleStep(0.1)
    assert sld.singleStep() == 0.1

    sld.setSingleStep(1.5e20)
    assert sld.singleStep() == 1.5e20

    sld.setPageStep(0.2)
    assert sld.pageStep() == 0.2

    sld.setPageStep(1.5e30)
    assert sld.pageStep() == 1.5e30


@pytest.mark.parametrize("mag", list(range(4, 37, 4)) + list(range(-4, -37, -4)))
@pytest.mark.parametrize("cls, orientation", FLOAT_SLIDERS)
def test_slider_extremes(cls, orientation, qtbot, mag):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    _mag = 10**mag
    with qtbot.waitSignal(sld.rangeChanged):
        sld.setRange(-_mag, _mag)
    for i in _linspace(-_mag, _mag, 10):
        sld.setValue((i, _mag))
        assert math.isclose(sld.value()[0], i, rel_tol=0.0001)
        sld.initStyleOption(QStyleOptionSlider())


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_ticks(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    sld.setTickInterval(0.3)
    assert sld.tickInterval() == 0.3
    sld.setTickPosition(sld.TickPosition.TicksAbove)
    sld.show()


@pytest.mark.parametrize("cls, orientation", FLOAT_SLIDERS)
def test_press_move_release(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    # this fail on vertical came with pyside6.2 ... need to debug
    # still works in practice, but test fails to catch signals
    if sld.orientation() == Qt.Orientation.Vertical:
        pytest.xfail()

    assert sld._pressedControl == QStyle.SubControl.SC_None

    opt = QStyleOptionSlider()
    sld.initStyleOption(opt)
    style = sld.style()
    hrect = style.subControlRect(
        QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle
    )
    handle_pos = sld.mapToGlobal(hrect.center())

    with qtbot.waitSignal(sld.sliderPressed):
        qtbot.mousePress(sld, Qt.MouseButton.LeftButton, pos=handle_pos)

    assert sld._pressedControl == QStyle.SubControl.SC_SliderHandle

    with qtbot.waitSignals([sld.sliderMoved, sld.valueChanged]):
        shift = (
            QPoint(0, -8)
            if sld.orientation() == Qt.Orientation.Vertical
            else QPoint(8, 0)
        )
        sld.mouseMoveEvent(_mouse_event(handle_pos + shift))

    with qtbot.waitSignal(sld.sliderReleased):
        qtbot.mouseRelease(sld, Qt.MouseButton.LeftButton, pos=handle_pos)

    assert sld._pressedControl == QStyle.SubControl.SC_None

    sld.show()
    with qtbot.waitSignal(sld.sliderPressed):
        qtbot.mousePress(sld, Qt.MouseButton.LeftButton, pos=handle_pos)


@skip_on_linux_qt6
@pytest.mark.parametrize("cls, orientation", FLOAT_SLIDERS)
def test_hover(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    hrect = sld._handleRect(0)
    handle_pos = QPointF(sld.mapToGlobal(hrect.center()))

    assert sld._hoverControl == QStyle.SubControl.SC_None

    sld.event(_hover_event(QEvent.Type.HoverEnter, handle_pos, QPointF(), sld))
    assert sld._hoverControl == QStyle.SubControl.SC_SliderHandle

    sld.event(
        _hover_event(QEvent.Type.HoverLeave, QPointF(-1000, -1000), handle_pos, sld)
    )
    assert sld._hoverControl == QStyle.SubControl.SC_None


@pytest.mark.parametrize("cls, orientation", FLOAT_SLIDERS)
def test_wheel(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    with qtbot.waitSignal(sld.valueChanged):
        sld.wheelEvent(_wheel_event(120))

    sld.wheelEvent(_wheel_event(0))


def _assert_types(args: Iterable[Any], type_: type):
    # sourcery skip: comprehension-to-generator
    assert all(isinstance(v, type_) for v in args), "invalid type"


@pytest.mark.parametrize("cls, orientation", ALL_SLIDER_COMBOS)
def test_rangeslider_signals(cls, orientation, qtbot):
    sld = cls(orientation)
    qtbot.addWidget(sld)

    type_ = float if cls == QDoubleRangeSlider else int

    mock = Mock()
    sld.valueChanged.connect(mock)
    with qtbot.waitSignal(sld.valueChanged):
        sld.setValue((20, 40))
    mock.assert_called_once_with((20, 40))
    _assert_types(mock.call_args.args, tuple)
    _assert_types(mock.call_args.args[0], type_)

    mock = Mock()
    sld.rangeChanged.connect(mock)
    with qtbot.waitSignal(sld.rangeChanged):
        sld.setMinimum(3)
    mock.assert_called_once_with(3, 99)
    _assert_types(mock.call_args.args, type_)

    mock.reset_mock()
    with qtbot.waitSignal(sld.rangeChanged):
        sld.setMaximum(15)
    mock.assert_called_once_with(3, 15)
    _assert_types(mock.call_args.args, type_)

    mock.reset_mock()
    with qtbot.waitSignal(sld.rangeChanged):
        sld.setRange(1, 2)
    mock.assert_called_once_with(1, 2)
    _assert_types(mock.call_args.args, type_)
