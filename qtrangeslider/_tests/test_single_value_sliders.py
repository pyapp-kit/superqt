import math
from contextlib import suppress
from distutils.version import LooseVersion

import pytest

from qtrangeslider import QDoubleSlider, QLabeledDoubleSlider, QLabeledSlider
from qtrangeslider._generic_slider import _GenericSlider
from qtrangeslider.qtcompat.QtCore import QEvent, QPoint, QPointF, Qt
from qtrangeslider.qtcompat.QtGui import QHoverEvent
from qtrangeslider.qtcompat.QtWidgets import QSlider, QStyle, QStyleOptionSlider

from ._testutil import (
    QT_VERSION,
    SYS_DARWIN,
    _linspace,
    _mouse_event,
    _wheel_event,
    skip_on_linux_qt6,
)


@pytest.fixture(params=[Qt.Horizontal, Qt.Vertical], ids=["horizontal", "vertical"])
def orientation(request):
    return request.param


START_MI_MAX_VAL = (0, 99, 0)
TEST_SLIDERS = [QDoubleSlider, QLabeledSlider, QLabeledDoubleSlider]


def _assert_value_in_range(sld):
    val = sld.value()
    if isinstance(val, (int, float)):
        val = (val,)
    assert all(sld.minimum() <= v <= sld.maximum() for v in val)


@pytest.fixture(params=TEST_SLIDERS)
def sld(request, qtbot, orientation):
    Cls = request.param
    slider = Cls(orientation)
    slider.setRange(*START_MI_MAX_VAL[:2])
    slider.setValue(START_MI_MAX_VAL[2])
    qtbot.addWidget(slider)
    assert (slider.minimum(), slider.maximum(), slider.value()) == START_MI_MAX_VAL
    _assert_value_in_range(slider)
    yield slider
    _assert_value_in_range(slider)
    with suppress(AttributeError):
        slider.initStyleOption(QStyleOptionSlider())


def called_with(*expected_result):
    """Use in check_params_cbs to assert that a callback is called as expected.

    e.g. `called_with(20, 50)` returns a callback that checks that the callback
    is called with the arguments (20, 50)
    """

    def check_emitted_values(*values):
        return values == expected_result

    return check_emitted_values


def test_change_floatslider_range(sld: _GenericSlider, qtbot):
    BOTH = [sld.rangeChanged, sld.valueChanged]

    for signals, checks, funcname, args in [
        (BOTH, [called_with(10, 99), called_with(10)], "setMinimum", (10,)),
        ([sld.rangeChanged], [called_with(10, 90)], "setMaximum", (90,)),
        (BOTH, [called_with(20, 40), called_with(20)], "setRange", (20, 40)),
        ([sld.valueChanged], [called_with(30)], "setValue", (30,)),
        (BOTH, [called_with(20, 25), called_with(25)], "setMaximum", (25,)),
        ([sld.valueChanged], [called_with(23)], "setValue", (23,)),
    ]:
        with qtbot.waitSignals(signals, check_params_cbs=checks, timeout=500):
            getattr(sld, funcname)(*args)
        _assert_value_in_range(sld)


def test_float_values(sld: _GenericSlider, qtbot):
    if type(sld) is QLabeledSlider:
        pytest.skip()
    for signals, checks, funcname, args in [
        (sld.rangeChanged, called_with(0.1, 0.9), "setRange", (0.1, 0.9)),
        (sld.valueChanged, called_with(0.4), "setValue", (0.4,)),
        (sld.valueChanged, called_with(0.1), "setValue", (0,)),
        (sld.valueChanged, called_with(0.9), "setValue", (1.9,)),
    ]:
        with qtbot.waitSignal(signals, check_params_cb=checks, timeout=400):
            getattr(sld, funcname)(*args)
        _assert_value_in_range(sld)


def test_ticks(sld: _GenericSlider, qtbot):
    sld.setTickInterval(3)
    assert sld.tickInterval() == 3
    sld.setTickPosition(QSlider.TicksAbove)
    sld.show()


# FIXME: this isn't testing labeled sliders as it needs to be ...
@pytest.mark.skipif(not SYS_DARWIN, reason="mousePress only working on mac")
def test_press_move_release(sld: _GenericSlider, qtbot):

    _real_sld = getattr(sld, "_slider", sld)

    with suppress(AttributeError):  # for QSlider
        assert _real_sld._pressedControl == QStyle.SubControl.SC_None

    opt = QStyleOptionSlider()
    _real_sld.initStyleOption(opt)
    style = _real_sld.style()
    hrect = style.subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle)
    handle_pos = _real_sld.mapToGlobal(hrect.center())

    with qtbot.waitSignal(_real_sld.sliderPressed, timeout=300):
        qtbot.mousePress(_real_sld, Qt.LeftButton, pos=handle_pos)

    with suppress(AttributeError):
        assert sld._pressedControl == QStyle.SubControl.SC_SliderHandle

    with qtbot.waitSignals(
        [_real_sld.sliderMoved, _real_sld.valueChanged], timeout=300
    ):
        shift = (
            QPoint(0, -8) if _real_sld.orientation() == Qt.Vertical else QPoint(8, 0)
        )
        _real_sld.mouseMoveEvent(_mouse_event(handle_pos + shift))

    with qtbot.waitSignal(_real_sld.sliderReleased, timeout=300):
        qtbot.mouseRelease(_real_sld, Qt.LeftButton, pos=handle_pos)

    with suppress(AttributeError):
        assert _real_sld._pressedControl == QStyle.SubControl.SC_None

    sld.show()
    with qtbot.waitSignal(_real_sld.sliderPressed, timeout=300):
        qtbot.mousePress(_real_sld, Qt.LeftButton, pos=handle_pos)


@skip_on_linux_qt6
def test_hover(sld: _GenericSlider):

    _real_sld = getattr(sld, "_slider", sld)

    opt = QStyleOptionSlider()
    _real_sld.initStyleOption(opt)
    hrect = _real_sld.style().subControlRect(
        QStyle.CC_Slider, opt, QStyle.SC_SliderHandle
    )
    handle_pos = QPointF(sld.mapToGlobal(hrect.center()))

    with suppress(AttributeError):  # for QSlider
        assert _real_sld._hoverControl == QStyle.SubControl.SC_None

    _real_sld.event(QHoverEvent(QEvent.HoverEnter, handle_pos, QPointF()))
    with suppress(AttributeError):  # for QSlider
        assert _real_sld._hoverControl == QStyle.SubControl.SC_SliderHandle

    _real_sld.event(QHoverEvent(QEvent.HoverLeave, QPointF(-1000, -1000), handle_pos))
    with suppress(AttributeError):  # for QSlider
        assert _real_sld._hoverControl == QStyle.SubControl.SC_None


def test_wheel(sld: _GenericSlider, qtbot):

    if type(sld) is QLabeledSlider and QT_VERSION < LooseVersion("5.12"):
        pytest.skip()

    _real_sld = getattr(sld, "_slider", sld)
    with qtbot.waitSignal(sld.valueChanged, timeout=400):
        _real_sld.wheelEvent(_wheel_event(120))

    _real_sld.wheelEvent(_wheel_event(0))


def test_position(sld: _GenericSlider, qtbot):
    sld.setSliderPosition(21)
    assert sld.sliderPosition() == 21

    if type(sld) is not QLabeledSlider:
        sld.setSliderPosition(21.5)
        assert sld.sliderPosition() == 21.5


def test_steps(sld: _GenericSlider, qtbot):

    sld.setSingleStep(11)
    assert sld.singleStep() == 11

    sld.setPageStep(16)
    assert sld.pageStep() == 16

    if type(sld) is not QLabeledSlider:

        sld.setSingleStep(0.1)
        assert sld.singleStep() == 0.1

        sld.setSingleStep(1.5e20)
        assert sld.singleStep() == 1.5e20

        sld.setPageStep(0.2)
        assert sld.pageStep() == 0.2

        sld.setPageStep(1.5e30)
        assert sld.pageStep() == 1.5e30


@pytest.mark.parametrize("mag", list(range(4, 37, 4)) + list(range(-4, -37, -4)))
def test_slider_extremes(sld: _GenericSlider, mag, qtbot):
    if type(sld) is QLabeledSlider:
        pytest.skip()

    _mag = 10 ** mag
    with qtbot.waitSignal(sld.rangeChanged, timeout=400):
        sld.setRange(-_mag, _mag)
    for i in _linspace(-_mag, _mag, 10):
        sld.setValue(i)
        assert math.isclose(sld.value(), i, rel_tol=1e-8)
