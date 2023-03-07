import math
import platform

import pytest
from qtpy.QtCore import QEvent, QPoint, QPointF, Qt
from qtpy.QtWidgets import QStyle, QStyleOptionSlider

from superqt.sliders._generic_slider import _GenericSlider, _sliderValueFromPosition

from ._testutil import _hover_event, _mouse_event, _wheel_event, skip_on_linux_qt6


@pytest.fixture(params=[Qt.Orientation.Horizontal, Qt.Orientation.Vertical])
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
    gslider.setTickPosition(gslider.TickPosition.TicksAbove)
    gslider.show()


def test_show(gslider, qtbot):
    gslider.show()


@pytest.mark.skipif(platform.system() != "Darwin", reason="cross-platform is tricky")
def test_press_move_release(gslider: _GenericSlider, qtbot):
    # this fail on vertical came with pyside6.2 ... need to debug
    # still works in practice, but test fails to catch signals
    if gslider.orientation() == Qt.Orientation.Vertical:
        pytest.xfail()

    assert gslider._pressedControl == QStyle.SubControl.SC_None

    opt = QStyleOptionSlider()
    gslider.initStyleOption(opt)
    style = gslider.style()
    hrect = style.subControlRect(
        QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle
    )
    handle_pos = gslider.mapToGlobal(hrect.center())

    with qtbot.waitSignal(gslider.sliderPressed):
        qtbot.mousePress(gslider, Qt.MouseButton.LeftButton, pos=handle_pos)

    assert gslider._pressedControl == QStyle.SubControl.SC_SliderHandle

    with qtbot.waitSignals([gslider.sliderMoved, gslider.valueChanged]):
        shift = (
            QPoint(0, -8)
            if gslider.orientation() == Qt.Orientation.Vertical
            else QPoint(8, 0)
        )
        gslider.mouseMoveEvent(_mouse_event(handle_pos + shift))

    with qtbot.waitSignal(gslider.sliderReleased):
        qtbot.mouseRelease(gslider, Qt.MouseButton.LeftButton, pos=handle_pos)

    assert gslider._pressedControl == QStyle.SubControl.SC_None

    gslider.show()
    with qtbot.waitSignal(gslider.sliderPressed):
        qtbot.mousePress(gslider, Qt.MouseButton.LeftButton, pos=handle_pos)


@skip_on_linux_qt6
def test_hover(gslider: _GenericSlider):
    # stub
    opt = QStyleOptionSlider()
    gslider.initStyleOption(opt)
    style = gslider.style()
    hrect = style.subControlRect(
        QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle
    )
    handle_pos = QPointF(gslider.mapToGlobal(hrect.center()))

    assert gslider._hoverControl == QStyle.SubControl.SC_None

    gslider.event(_hover_event(QEvent.Type.HoverEnter, handle_pos, QPointF(), gslider))
    assert gslider._hoverControl == QStyle.SubControl.SC_SliderHandle

    gslider.event(
        _hover_event(QEvent.Type.HoverLeave, QPointF(-1000, -1000), handle_pos, gslider)
    )
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


# args are (min: float, max: float, position: int, span: int, upsideDown: bool)
@pytest.mark.parametrize(
    "args, result",
    [
        # (min, max, pos, span[, inverted]), expectation
        # data range (1, 2)
        ((1, 2, 50, 100), 1.5),
        ((1, 2, 70, 100), 1.7),
        ((1, 2, 70, 100, True), 1.3),  # inverted appearance
        ((1, 2, 170, 100), 2),
        ((1, 2, 100, 100), 2),
        ((1, 2, -30, 100), 1),
        # data range (-2, 2)
        ((-2, 2, 50, 100), 0),
        ((-2, 2, 75, 100), 1),
        ((-2, 2, 75, 100, True), -1),  # inverted appearance
        ((-2, 2, 170, 100), 2),
        ((-2, 2, 100, 100), 2),
        ((-2, 2, -30, 100), -2),
    ],
)
def test_slider_value_from_position(args, result):
    assert math.isclose(_sliderValueFromPosition(*args), result)
