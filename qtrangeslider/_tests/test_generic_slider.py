import math

import pytest

from qtrangeslider._generic_slider import _GenericSlider
from qtrangeslider.qtcompat.QtCore import QEvent, QPoint, QPointF, Qt
from qtrangeslider.qtcompat.QtGui import QHoverEvent
from qtrangeslider.qtcompat.QtWidgets import QStyle, QStyleOptionSlider

from ._testutil import _linspace, _mouse_event, _wheel_event, skip_on_linux_qt6


@pytest.fixture(params=[Qt.Horizontal, Qt.Vertical])
def gslider(qtbot, request):
    slider = _GenericSlider(request.param)
    qtbot.addWidget(slider)
    assert slider.value() == 0
    assert slider.minimum() == 0
    assert slider.maximum() == 99
    yield slider
    slider.initStyleOption(QStyleOptionSlider())


def test_change_floatslider_range(gslider: _GenericSlider, qtbot):
    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setMinimum(10)

    assert gslider.value() == 10 == gslider.minimum()
    assert gslider.maximum() == 99

    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setMaximum(90)
    assert gslider.value() == 10 == gslider.minimum()
    assert gslider.maximum() == 90

    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setRange(20, 40)
    assert gslider.value() == 20 == gslider.minimum()
    assert gslider.maximum() == 40

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue(30)
    assert gslider.value() == 30

    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setMaximum(25)
    assert gslider.value() == 25 == gslider.maximum()
    assert gslider.minimum() == 20


def test_float_values(gslider: _GenericSlider, qtbot):
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setRange(0.25, 0.75)
    assert gslider.minimum() == 0.25
    assert gslider.maximum() == 0.75

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue(0.55)
    assert gslider.value() == 0.55

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue(1.55)
    assert gslider.value() == 0.75 == gslider.maximum()


def test_ticks(gslider: _GenericSlider, qtbot):
    gslider.setTickInterval(0.3)
    assert gslider.tickInterval() == 0.3
    gslider.setTickPosition(gslider.TicksAbove)
    gslider.show()


def test_show(gslider, qtbot):
    gslider.show()


def test_press_move_release(gslider: _GenericSlider, qtbot):
    assert gslider._pressedControl == QStyle.SubControl.SC_None

    opt = QStyleOptionSlider()
    gslider.initStyleOption(opt)
    style = gslider.style()
    hrect = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle)
    handle_pos = gslider.mapToGlobal(hrect.center())

    with qtbot.waitSignal(gslider.sliderPressed):
        qtbot.mousePress(gslider, Qt.LeftButton, pos=handle_pos)

    assert gslider._pressedControl == QStyle.SubControl.SC_SliderHandle

    with qtbot.waitSignals([gslider.sliderMoved, gslider.valueChanged]):
        shift = QPoint(0, -8) if gslider.orientation() == Qt.Vertical else QPoint(8, 0)
        gslider.mouseMoveEvent(_mouse_event(handle_pos + shift))

    with qtbot.waitSignal(gslider.sliderReleased):
        qtbot.mouseRelease(gslider, Qt.LeftButton, pos=handle_pos)

    assert gslider._pressedControl == QStyle.SubControl.SC_None

    gslider.show()
    with qtbot.waitSignal(gslider.sliderPressed):
        qtbot.mousePress(gslider, Qt.LeftButton, pos=handle_pos)


@skip_on_linux_qt6
def test_hover(gslider: _GenericSlider):

    opt = QStyleOptionSlider()
    gslider.initStyleOption(opt)
    style = gslider.style()
    hrect = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle)
    handle_pos = QPointF(gslider.mapToGlobal(hrect.center()))

    assert gslider._hoverControl == QStyle.SubControl.SC_None

    gslider.event(QHoverEvent(QEvent.HoverEnter, handle_pos, QPointF()))
    assert gslider._hoverControl == QStyle.SubControl.SC_SliderHandle

    gslider.event(QHoverEvent(QEvent.HoverLeave, QPointF(-1000, -1000), handle_pos))
    assert gslider._hoverControl == QStyle.SubControl.SC_None


def test_wheel(gslider: _GenericSlider, qtbot):
    with qtbot.waitSignal(gslider.valueChanged):
        gslider.wheelEvent(_wheel_event(120))

    gslider.wheelEvent(_wheel_event(0))


def test_position(gslider: _GenericSlider, qtbot):
    gslider.setSliderPosition(21.2)
    assert gslider.sliderPosition() == 21.2


def test_steps(gslider: _GenericSlider, qtbot):
    gslider.setSingleStep(0.1)
    assert gslider.singleStep() == 0.1

    gslider.setSingleStep(1.5e20)
    assert gslider.singleStep() == 1.5e20

    gslider.setPageStep(0.2)
    assert gslider.pageStep() == 0.2

    gslider.setPageStep(1.5e30)
    assert gslider.pageStep() == 1.5e30


@pytest.mark.parametrize("mag", list(range(4, 37, 4)) + list(range(-4, -37, -4)))
def test_slider_extremes(gslider: _GenericSlider, mag, qtbot):
    _mag = 10 ** mag
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setRange(-_mag, _mag)
    for i in _linspace(-_mag, _mag, 10):
        gslider.setValue(i)
        assert math.isclose(gslider.value(), i, rel_tol=1e-8)
        gslider.initStyleOption(QStyleOptionSlider())
