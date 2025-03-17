from unittest.mock import Mock

from qtpy.QtCore import Qt

from superqt import QToggleSwitch


def test_on_and_off(qtbot):
    wdg = QToggleSwitch()
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


def test_widget_size(qtbot):
    wdg = QToggleSwitch()
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
    mock = Mock()
    wdg.toggled.connect(mock)
    qtbot.addWidget(wdg)
    assert not wdg.isChecked()
    mock.assert_not_called()
    qtbot.mouseClick(wdg._text_label, Qt.MouseButton.LeftButton)
    assert wdg.isChecked()
    mock.assert_called_once_with(True)
    qtbot.mouseClick(wdg._text_label, Qt.MouseButton.LeftButton)
    assert not wdg.isChecked()

    mock.reset_mock()
    qtbot.mouseClick(wdg._switch, Qt.MouseButton.LeftButton)
    assert wdg.isChecked()
    mock.assert_called_once_with(True)
    qtbot.mouseClick(wdg._switch, Qt.MouseButton.LeftButton)
    assert not wdg.isChecked()
