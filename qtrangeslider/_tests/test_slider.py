import platform

import pytest

from qtrangeslider import QRangeSlider
from qtrangeslider._generic_range_slider import SC_BAR, SC_HANDLE, SC_NONE
from qtrangeslider.qtcompat import API_NAME
from qtrangeslider.qtcompat.QtCore import Qt

NOT_LINUX = platform.system() != "Linux"
NOT_PYSIDE2 = API_NAME != "PySide2"

skipmouse = pytest.mark.skipif(NOT_LINUX or NOT_PYSIDE2, reason="mouse tests finicky")


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_basic(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_value(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)
    rs.setValue([10, 20])
    assert rs.value() == (10, 20)


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_range(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)
    rs.setValue([10, 20])
    assert rs.value() == (10, 20)
    rs.setRange(15, 20)
    assert rs.value() == (15, 20)
    assert rs.minimum() == 15
    assert rs.maximum() == 20


@skipmouse
def test_drag_handles(qtbot):
    rs = QRangeSlider(Qt.Horizontal)
    qtbot.addWidget(rs)
    rs.setRange(0, 99)
    rs.setValue((20, 80))
    rs.setMouseTracking(True)
    rs.show()

    # press the left handle
    pos = rs._handleRect(0).center()
    with qtbot.waitSignal(rs.sliderPressed):
        qtbot.mousePress(rs, Qt.LeftButton, pos=pos)
    assert rs._pressedControl == SC_HANDLE
    assert rs._pressedIndex == 0

    # drag the left handle
    with qtbot.waitSignals([rs.sliderMoved] * 13):  # couple less signals
        for _ in range(15):
            pos.setX(pos.x() + 2)
            qtbot.mouseMove(rs, pos)

    with qtbot.waitSignal(rs.sliderReleased):
        qtbot.mouseRelease(rs, Qt.LeftButton)

    # check the values
    assert rs.value()[0] > 30
    assert rs._pressedControl == SC_NONE

    # press the right handle
    pos = rs._handleRect(1).center()
    with qtbot.waitSignal(rs.sliderPressed):
        qtbot.mousePress(rs, Qt.LeftButton, pos=pos)
    assert rs._pressedControl == SC_HANDLE
    assert rs._pressedIndex == 1

    # drag the right handle
    with qtbot.waitSignals([rs.sliderMoved] * 13):  # couple less signals
        for _ in range(15):
            pos.setX(pos.x() - 2)
            qtbot.mouseMove(rs, pos)
    with qtbot.waitSignal(rs.sliderReleased):
        qtbot.mouseRelease(rs, Qt.LeftButton)

    # check the values
    assert rs.value()[1] < 70
    assert rs._pressedControl == SC_NONE


@skipmouse
def test_drag_handles_beyond_edge(qtbot):
    rs = QRangeSlider(Qt.Horizontal)
    qtbot.addWidget(rs)
    rs.setRange(0, 99)
    rs.setValue((20, 80))
    rs.setMouseTracking(True)
    rs.show()

    # press the right handle
    pos = rs._handleRect(1).center()
    with qtbot.waitSignal(rs.sliderPressed):
        qtbot.mousePress(rs, Qt.LeftButton, pos=pos)
    assert rs._pressedControl == SC_HANDLE
    assert rs._pressedIndex == 1

    # drag the handle off the right edge and make sure the value gets to the max
    for _ in range(7):
        pos.setX(pos.x() + 10)
        qtbot.mouseMove(rs, pos)

    with qtbot.waitSignal(rs.sliderReleased):
        qtbot.mouseRelease(rs, Qt.LeftButton)

    assert rs.value()[1] == 99


@skipmouse
def test_bar_drag_beyond_edge(qtbot):
    rs = QRangeSlider(Qt.Horizontal)
    qtbot.addWidget(rs)
    rs.setRange(0, 99)
    rs.setValue((20, 80))
    rs.setMouseTracking(True)
    rs.show()

    # press the right handle
    pos = rs.rect().center()
    with qtbot.waitSignal(rs.sliderPressed):
        qtbot.mousePress(rs, Qt.LeftButton, pos=pos)
    assert rs._pressedControl == SC_BAR
    assert rs._pressedIndex == 1

    # drag the handle off the right edge and make sure the value gets to the max
    for _ in range(15):
        pos.setX(pos.x() + 10)
        qtbot.mouseMove(rs, pos)

    with qtbot.waitSignal(rs.sliderReleased):
        qtbot.mouseRelease(rs, Qt.LeftButton)

    assert rs.value()[1] == 99
