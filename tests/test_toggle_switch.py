import pytest
from qtpy.QtCore import Qt

from superqt import QLabeledToggleSwitch, QToggleSwitch


@pytest.mark.parametrize("qtwidget_class", [QToggleSwitch, QLabeledToggleSwitch])
def test_on_and_off(qtbot, qtwidget_class):
    wdg = qtwidget_class()
    qtbot.addWidget(wdg)
    assert not wdg.isChecked()
    wdg.setChecked(True)
    assert wdg.isChecked()
    wdg.setChecked(False)
    assert not wdg.isChecked()
    wdg.toggle()
    assert wdg.isChecked()
    wdg.toggle()
    assert not wdg.isChecked()


@pytest.mark.parametrize("qtwidget_class", [QToggleSwitch, QLabeledToggleSwitch])
def test_widget_size(qtbot, qtwidget_class):
    wdg = qtwidget_class()
    qtbot.addWidget(wdg)
    wdg.setSize(20)
    assert wdg.size() == 20
    wdg.toggle()
    wdg.setSize(10)
    assert wdg.size() == 10
    wdg.toggle()


def test_get_set_color(qtbot):
    wdg = QToggleSwitch()
    qtbot.addWidget(wdg)
    wdg.onColor = "#ff0000"
    assert wdg.onColor.name() == "#ff0000"
    wdg.offColor = "#00ff00"
    assert wdg.offColor.name() == "#00ff00"
    wdg.handleColor = "#0000ff"
    assert wdg.handleColor.name() == "#0000ff"


def test_mouse_click(qtbot):
    wdg = QToggleSwitch()
    qtbot.addWidget(wdg)
    assert not wdg.isChecked()
    qtbot.mouseClick(wdg, Qt.MouseButton.LeftButton)
    assert wdg.isChecked()
    qtbot.mouseClick(wdg, Qt.MouseButton.LeftButton)
    assert not wdg.isChecked()

    wdg = QLabeledToggleSwitch()
    qtbot.addWidget(wdg)
    assert not wdg.isChecked()
    qtbot.mouseClick(wdg._text_label, Qt.MouseButton.LeftButton)
    assert wdg.isChecked()
    qtbot.mouseClick(wdg._text_label, Qt.MouseButton.LeftButton)
    assert not wdg.isChecked()
