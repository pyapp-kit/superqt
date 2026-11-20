from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from qtpy import QtWidgets
from qtpy.QtWidgets import QApplication

from superqt.fonticon._plugins import FontIconManager
from superqt.fonticon._qfont_icon import QFontIconStore

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytestqt.qtbot import QtBot

ROOT = Path(__file__).parent.parent
EXAMPLES = sorted([*ROOT.glob("docs/examples/*.py"), *ROOT.glob("examples/*.py")])


class _App:
    """What an example gets for `QApplication([])`: the running app, whose `exec`
    returns at once."""

    def __init__(self, app: QApplication) -> None:
        self._app = app

    def exec(self, *_: Any) -> int:
        return 0

    exec_ = exec

    def __getattr__(self, name: str) -> Any:
        return getattr(self._app, name)


class _AppClass(type):
    def __call__(cls, *_: Any, **__: Any) -> _App:
        return _App(QApplication.instance())

    def __getattr__(cls, name: str) -> Any:  # (static methods, enums, ...)
        return getattr(QApplication, name)


class _QApplication(metaclass=_AppClass):
    pass


@pytest.fixture(autouse=True)
def _unload_fonts(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Unload the font packs that examples load (other tests expect none)."""
    monkeypatch.setattr(FontIconManager, "_LOADED", {})
    yield
    QFontIconStore.clear()


@pytest.mark.parametrize(
    "path", EXAMPLES, ids=[str(p.relative_to(ROOT)) for p in EXAMPLES]
)
def test_example(
    path: Path, qapp: QApplication, qtbot: QtBot, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(QtWidgets, "QApplication", _QApplication)
    before = set(QApplication.topLevelWidgets())
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(path)}  # (keeps widgets)
    try:
        exec(code, namespace)
    except ModuleNotFoundError as e:
        pytest.skip(f"needs {e.name or e}")
    except SystemExit:
        pass
    finally:
        # (hidden ones, like a completer's popup, are deleted with their owner)
        shown = [
            w
            for w in QApplication.topLevelWidgets()
            if w not in before and w.isVisible() and w.parent() is None
        ]
        for window in shown:
            qtbot.addWidget(window)  # (closed and deleted after the test)

    # (the docs render each of their examples' window)
    if path.parent.parent.name == "docs":
        assert len(shown) == 1, f"shows {len(shown)} windows, not 1"
    else:
        assert shown, "shows no window"
