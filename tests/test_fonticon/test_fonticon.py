from pathlib import Path

import pytest
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import QPushButton

from superqt.fonticon import icon, pulse, setTextIcon, spin
from superqt.fonticon._qfont_icon import QFontIconStore, _ensure_identifier

TEST_PREFIX = "ico"
TEST_CHARNAME = "smiley"
TEST_CHAR = "\ue900"
TEST_GLYPHKEY = f"{TEST_PREFIX}.{TEST_CHARNAME}"
FONT_FILE = Path(__file__).parent / "fixtures" / "fake_plugin" / "icontest.ttf"


@pytest.fixture
def store(qapp):
    store = QFontIconStore().instance()
    yield store
    store.clear()


@pytest.fixture
def full_store(store):
    store.addFont(str(FONT_FILE), TEST_PREFIX, {TEST_CHARNAME: TEST_CHAR})
    return store


def test_no_font_key():
    with pytest.raises(KeyError) as err:
        icon(TEST_GLYPHKEY)
        assert "Unrecognized font key: {TEST_PREFIX!r}." in str(err)


def test_no_charmap(store):
    store.addFont(str(FONT_FILE), TEST_PREFIX)
    with pytest.raises(KeyError) as err:
        icon(TEST_GLYPHKEY)
        assert "No charmap registered for" in str(err)


def test_font_icon_works(full_store):
    icn = icon(TEST_GLYPHKEY)
    assert isinstance(icn, QIcon)
    assert isinstance(icn.pixmap(40, 40), QPixmap)

    icn = icon(f"{TEST_PREFIX}.{TEST_CHAR}")  # also works with unicode key
    assert isinstance(icn, QIcon)
    assert isinstance(icn.pixmap(40, 40), QPixmap)

    with pytest.raises(ValueError) as err:
        icon(f"{TEST_PREFIX}.smelly")  # bad name
        assert "Font 'test (Regular)' has no glyph with the key 'smelly'" in str(err)


def test_on_button(full_store, qtbot):
    btn = QPushButton(None)
    qtbot.addWidget(btn)
    btn.setIcon(icon(TEST_GLYPHKEY))


def test_btn_text_icon(full_store, qtbot):
    btn = QPushButton(None)
    qtbot.addWidget(btn)
    setTextIcon(btn, TEST_GLYPHKEY)
    assert btn.text() == TEST_CHAR


def test_animation(full_store, qtbot):
    btn = QPushButton(None)
    qtbot.addWidget(btn)
    icn = icon(TEST_GLYPHKEY, animation=pulse(btn))
    btn.setIcon(icn)
    with qtbot.waitSignal(icn._engine._default_opts.animation.timer.timeout):
        icn.pixmap(40, 40)
        btn.update()


def test_multistate(full_store, qtbot, qapp):
    """complicated multistate icon"""
    btn = QPushButton()
    qtbot.addWidget(btn)
    icn = icon(
        TEST_GLYPHKEY,
        color="blue",
        states={
            "active": {
                "color": "red",
                "scale_factor": 0.5,
                "animation": pulse(btn),
            },
            "disabled": {
                "color": "green",
                "scale_factor": 0.8,
                "animation": spin(btn),
            },
        },
    )
    btn.setIcon(icn)
    btn.show()

    btn.setEnabled(False)
    active = icn._engine._opts[QIcon.State.Off][QIcon.Mode.Active].animation.timer
    disabled = icn._engine._opts[QIcon.State.Off][QIcon.Mode.Disabled].animation.timer

    with qtbot.waitSignal(active.timeout, timeout=1000):
        btn.setEnabled(True)
        # hack to get the signal emitted
        icn.pixmap(100, 100, QIcon.Mode.Active, QIcon.State.Off)

    assert active.isActive()
    assert not disabled.isActive()
    with qtbot.waitSignal(disabled.timeout):
        btn.setEnabled(False)
    assert disabled.isActive()

    # smoke test, paint all the states
    icn.pixmap(100, 100, QIcon.Mode.Active, QIcon.State.Off)
    icn.pixmap(100, 100, QIcon.Mode.Disabled, QIcon.State.Off)
    icn.pixmap(100, 100, QIcon.Mode.Selected, QIcon.State.Off)
    icn.pixmap(100, 100, QIcon.Mode.Normal, QIcon.State.Off)
    icn.pixmap(100, 100, QIcon.Mode.Active, QIcon.State.On)
    icn.pixmap(100, 100, QIcon.Mode.Disabled, QIcon.State.On)
    icn.pixmap(100, 100, QIcon.Mode.Selected, QIcon.State.On)
    icn.pixmap(100, 100, QIcon.Mode.Normal, QIcon.State.On)


def test_ensure_identifier():
    assert _ensure_identifier("") == ""
    assert _ensure_identifier("1a") == "_1a"
    assert _ensure_identifier("from") == "from_"
    assert _ensure_identifier("hello-world") == "hello_world"
    assert _ensure_identifier("hello_world") == "hello_world"
    assert _ensure_identifier("hello world") == "hello_world"
