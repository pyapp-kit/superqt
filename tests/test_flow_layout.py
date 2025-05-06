from typing import Any

from qtpy.QtWidgets import QPushButton, QWidget

from superqt import QFlowLayout


def test_flow_layout(qtbot: Any) -> None:
    wdg = QWidget()
    qtbot.addWidget(wdg)

    layout = QFlowLayout(wdg)
    layout.addWidget(QPushButton("Short"))
    layout.addWidget(QPushButton("Longer"))
    layout.addWidget(QPushButton("Different text"))
    layout.addWidget(QPushButton("More text"))
    layout.addWidget(QPushButton("Even longer button text"))

    wdg.setWindowTitle("Flow Layout")
    wdg.show()

    assert layout.expandingDirections()
    assert layout.heightForWidth(200) > layout.heightForWidth(400)
    assert layout.count() == 5
    assert layout.itemAt(0).widget().text() == "Short"
    layout.takeAt(0)
    assert layout.count() == 4
