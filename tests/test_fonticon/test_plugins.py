import sys
from pathlib import Path

import pytest
from qtpy.QtGui import QIcon, QPixmap

from superqt.fonticon import _plugins, icon
from superqt.fonticon._qfont_icon import QFontIconStore

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def plugin_store(qapp, monkeypatch):
    _path = [str(FIXTURES), *sys.path.copy()]
    store = QFontIconStore().instance()
    with monkeypatch.context() as m:
        m.setattr(sys, "path", _path)
        yield store
    store.clear()


def test_plugin(plugin_store):
    assert not _plugins.loaded()
    icn = icon("ico.smiley")
    assert _plugins.loaded() == {"ico": ["smiley"]}
    assert isinstance(icn, QIcon)
    assert isinstance(icn.pixmap(40, 40), QPixmap)
