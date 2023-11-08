from typing import TYPE_CHECKING

import pytest
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QPushButton

from superqt import QIconifyIcon

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_qiconify(qtbot: "QtBot", monkeypatch: "pytest.MonkeyPatch") -> None:
    monkeypatch.setenv("PYCONIFY_CACHE", "0")
    pytest.importorskip("pyconify")

    icon = QIconifyIcon("bi:alarm-fill", color="red", flip="vertical")
    icon.addKey("bi:alarm", color="blue", rotate=90, state=QIcon.State.On)

    btn = QPushButton()
    qtbot.addWidget(btn)
    btn.setIcon(icon)
    btn.show()
