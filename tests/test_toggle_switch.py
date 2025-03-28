from unittest.mock import Mock

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QWidget

from superqt import QToggleSwitch


def test_on_and_off(qtbot):
    wdg = QToggleSwitch()
    qtbot.addWidget(wdg)
    wdg.show()
    assert not wdg.isChecked()
    wdg.setChecked(True)
    assert wdg.isChecked()
    QApplication.processEvents()
    wdg.setChecked(False)
    assert not wdg.isChecked()
    QApplication.processEvents()
    wdg.setChecked(False)
    assert not wdg.isChecked()
    wdg.toggle()
    assert wdg.isChecked()
    wdg.toggle()
    assert not wdg.isChecked()
    wdg.click()
    assert wdg.isChecked()
    wdg.click()
    assert not wdg.isChecked()
    QApplication.processEvents()


def test_get_set(qtbot):
    wdg = QToggleSwitch()
    qtbot.addWidget(wdg)
    wdg.onColor = "#ff0000"
    assert wdg.onColor.name() == "#ff0000"
    wdg.offColor = "#00ff00"
    assert wdg.offColor.name() == "#00ff00"
    wdg.handleColor = "#0000ff"
    assert wdg.handleColor.name() == "#0000ff"
    wdg.setText("new text")
    assert wdg.text() == "new text"
    wdg.switchWidth = 100
    assert wdg.switchWidth == 100
    wdg.switchHeight = 100
    assert wdg.switchHeight == 100
    wdg.handleSize = 80
    assert wdg.handleSize == 80


def test_mouse_click(qtbot):
    wdg = QToggleSwitch()
    mock = Mock()
    wdg.toggled.connect(mock)
    qtbot.addWidget(wdg)
    assert not wdg.isChecked()
    mock.assert_not_called()
    qtbot.mouseClick(wdg, Qt.MouseButton.LeftButton)
    assert wdg.isChecked()
    mock.assert_called_once_with(True)
    qtbot.mouseClick(wdg, Qt.MouseButton.LeftButton)
    assert not wdg.isChecked()


def test_signal_emission_order(qtbot):
    """Check if event emmision is same for QToggleSwitch and QCheckBox"""
    wdg = QToggleSwitch()
    emitted_from_toggleswitch = []
    wdg.toggled.connect(lambda: emitted_from_toggleswitch.append("toggled"))
    wdg.pressed.connect(lambda: emitted_from_toggleswitch.append("pressed"))
    wdg.clicked.connect(lambda: emitted_from_toggleswitch.append("clicked"))
    wdg.released.connect(lambda: emitted_from_toggleswitch.append("released"))
    qtbot.addWidget(wdg)

    checkbox = QCheckBox()
    emitted_from_checkbox = []
    checkbox.toggled.connect(lambda: emitted_from_checkbox.append("toggled"))
    checkbox.pressed.connect(lambda: emitted_from_checkbox.append("pressed"))
    checkbox.clicked.connect(lambda: emitted_from_checkbox.append("clicked"))
    checkbox.released.connect(lambda: emitted_from_checkbox.append("released"))
    qtbot.addWidget(checkbox)

    emitted_from_toggleswitch.clear()
    emitted_from_checkbox.clear()
    wdg.toggle()
    checkbox.toggle()
    assert emitted_from_toggleswitch
    assert emitted_from_toggleswitch == emitted_from_checkbox

    emitted_from_toggleswitch.clear()
    emitted_from_checkbox.clear()
    wdg.click()
    checkbox.click()
    assert emitted_from_toggleswitch
    assert emitted_from_toggleswitch == emitted_from_checkbox


def test_multiple_lines(qtbot):
    container = QWidget()
    layout = QVBoxLayout(container)
    wdg0 = QToggleSwitch("line1\nline2\nline3")
    wdg1 = QToggleSwitch("line1\nline2")
    checkbox = QCheckBox()
    layout.addWidget(wdg0)
    layout.addWidget(wdg1)
    layout.addWidget(checkbox)
    container.show()
    qtbot.addWidget(container)

    assert wdg0.text() == "line1\nline2\nline3"
    assert wdg1.text() == "line1\nline2"
    assert wdg0.sizeHint().height() > wdg1.sizeHint().height()
    assert wdg1.sizeHint().height() > checkbox.sizeHint().height()
    assert wdg0.height() > wdg1.height()
    assert wdg1.height() > checkbox.height()
