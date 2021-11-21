import sys
from pathlib import Path

import pytest

from superqt.fonticon import _plugins, icon
from superqt.fonticon._qfont_icon import QFontIconStore
from superqt.qtcompat.QtGui import QIcon, QPixmap

try:
    from importlib.metadata import Distribution
except ImportError:
    from importlib_metadata import Distribution  # type: ignore


class ICO:
    __font_file__ = str(Path(__file__).parent / "icontest.ttf")
    smiley = "ico.\ue900"


@pytest.fixture
def plugin_store(qapp, monkeypatch):
    class MockEntryPoint:
        name = "ico"
        group = _plugins.FontIconManager.ENTRY_POINT
        value = "fake_plugin.ICO"

        def load(self):
            return ICO

    class MockFinder:
        def find_distributions(self, *a):
            class D(Distribution):
                name = "mock"

                @property
                def entry_points(self):
                    return [MockEntryPoint()]

            return [D()]

    store = QFontIconStore().instance()
    with monkeypatch.context() as m:
        m.setattr(sys, "meta_path", [MockFinder()])
        yield store
    store.clear()


def test_plugin(plugin_store):
    assert not _plugins.loaded()
    icn = icon("ico.smiley")
    assert _plugins.loaded() == {"ico": ["smiley"]}
    assert isinstance(icn, QIcon)
    assert isinstance(icn.pixmap(40, 40), QPixmap)
