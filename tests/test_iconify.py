import pytest
from qtpy.QtWidgets import QPushButton

from superqt import QIconifyIcon


def test_qiconify(qtbot):
    pytest.importorskip("pyconify")
    icon = QIconifyIcon("bi:alarm-fill", color="red", rotate=90)
    assert icon.path.endswith(".svg")
    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon)
    btn.show()
