import pytest
from qtpy.QtWidgets import QPushButton

from superqt import QIconifyIcon


def test_qiconify(qtbot, tmp_path, monkeypatch):
    monkeypatch.setenv("PYCONIFY_CACHE", "0")

    pytest.importorskip("pyconify")
    icon = QIconifyIcon("bi:alarm-fill", color="red", rotate=90, dir=tmp_path)
    assert icon.path.name.endswith(".svg")
    assert icon.path.parent == tmp_path
    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon)
    btn.show()
