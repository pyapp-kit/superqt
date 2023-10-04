from typing import TYPE_CHECKING

import pytest
from qtpy.QtWidgets import QPushButton

from superqt import QIconifyIcon

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_qiconify(qtbot: "QtBot", monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setenv("PYCONIFY_CACHE", "0")
    pytest.importorskip("pyconify")

    icon = QIconifyIcon("bi:alarm-fill", color="red", rotate=90)
    assert icon.path.name.endswith(".svg")

    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon)
    btn.show()
