import math

import pytest

from qtrangeslider import QDoubleRangeSlider, QRangeSlider
from qtrangeslider.qtcompat.QtCore import QEvent, QPoint, QPointF, Qt
from qtrangeslider.qtcompat.QtGui import QHoverEvent
from qtrangeslider.qtcompat.QtWidgets import QStyle, QStyleOptionSlider

from ._testutil import _linspace, _mouse_event, _wheel_event, skip_on_linux_qt6


@pytest.fixture(params=[Qt.Horizontal, Qt.Vertical])
def gslider(qtbot, request):
    slider = QDoubleRangeSlider(request.param)
    qtbot.addWidget(slider)
    assert slider.value() == (20, 80)
    assert slider.minimum() == 0
    assert slider.maximum() == 99
    yield slider
    slider.initStyleOption(QStyleOptionSlider())


def test_change_floatslider_range(gslider: QRangeSlider, qtbot):
    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setMinimum(30)

    assert gslider.value()[0] == 30 == gslider.minimum()
    assert gslider.maximum() == 99

    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setMaximum(70)
    assert gslider.value()[0] == 30 == gslider.minimum()
    assert gslider.value()[1] == 70 == gslider.maximum()

    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setRange(40, 60)
    assert gslider.value()[0] == 40 == gslider.minimum()
    assert gslider.maximum() == 60

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue([40, 50])
    assert gslider.value()[0] == 40 == gslider.minimum()
    assert gslider.value()[1] == 50

    with qtbot.waitSignals([gslider.rangeChanged, gslider.valueChanged]):
        gslider.setMaximum(45)
    assert gslider.value()[0] == 40 == gslider.minimum()
    assert gslider.value()[1] == 45 == gslider.maximum()


def test_float_values(gslider: QRangeSlider, qtbot):
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setRange(0.1, 0.9)
    assert gslider.minimum() == 0.1
    assert gslider.maximum() == 0.9

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue([0.4, 0.6])
    assert gslider.value() == (0.4, 0.6)

    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue([0, 1.9])
    assert gslider.value()[0] == 0.1 == gslider.minimum()
    assert gslider.value()[1] == 0.9 == gslider.maximum()


def test_position(gslider: QRangeSlider, qtbot):
    gslider.setSliderPosition([10, 80])
    assert gslider.sliderPosition() == (10, 80)


def test_steps(gslider: QRangeSlider, qtbot):
    gslider.setSingleStep(0.1)
    assert gslider.singleStep() == 0.1

    gslider.setSingleStep(1.5e20)
    assert gslider.singleStep() == 1.5e20

    gslider.setPageStep(0.2)
    assert gslider.pageStep() == 0.2

    gslider.setPageStep(1.5e30)
    assert gslider.pageStep() == 1.5e30


@pytest.mark.parametrize("mag", list(range(4, 37, 4)) + list(range(-4, -37, -4)))
def test_slider_extremes(gslider: QRangeSlider, mag, qtbot):
    _mag = 10 ** mag
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setRange(-_mag, _mag)
    for i in _linspace(-_mag, _mag, 10):
        gslider.setValue((i, _mag))
        assert math.isclose(gslider.value()[0], i, rel_tol=1e-8)
        gslider.initStyleOption(QStyleOptionSlider())


def test_ticks(gslider: QRangeSlider, qtbot):
    gslider.setTickInterval(0.3)
    assert gslider.tickInterval() == 0.3
    gslider.setTickPosition(gslider.TicksAbove)
    gslider.show()


def test_show(gslider, qtbot):
    gslider.show()


def test_press_move_release(gslider: QRangeSlider, qtbot):
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
def test_hover(gslider: QRangeSlider):

    hrect = gslider._handleRect(0)
    handle_pos = QPointF(gslider.mapToGlobal(hrect.center()))

    assert gslider._hoverControl == QStyle.SubControl.SC_None

    gslider.event(QHoverEvent(QEvent.HoverEnter, handle_pos, QPointF()))
    assert gslider._hoverControl == QStyle.SubControl.SC_SliderHandle

    gslider.event(QHoverEvent(QEvent.HoverLeave, QPointF(-1000, -1000), handle_pos))
    assert gslider._hoverControl == QStyle.SubControl.SC_None


def test_wheel(gslider: QRangeSlider, qtbot):
    with qtbot.waitSignal(gslider.valueChanged):
        gslider.wheelEvent(_wheel_event(120))

    gslider.wheelEvent(_wheel_event(0))
