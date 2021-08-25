from superqt import QElidingLabel
from superqt.qtcompat.QtCore import QSize, Qt
from superqt.qtcompat.QtGui import QResizeEvent

TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
    "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad "
    "minim ven iam, quis nostrud exercitation ullamco laborisnisi ut aliquip "
    "ex ea commodo consequat. Duis aute irure dolor inreprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nullapariatur."
)
ELLIPSIS = "…"


def test_eliding_label(qtbot):
    wdg = QElidingLabel(TEXT)
    qtbot.addWidget(wdg)
    assert wdg._elidedText().endswith(ELLIPSIS)
    oldsize = wdg.size()
    newsize = QSize(200, 20)
    wdg.resize(newsize)
    wdg.resizeEvent(QResizeEvent(oldsize, newsize))  # for test coverage
    assert wdg.text() == TEXT


def test_wrapped_eliding_label(qtbot):
    wdg = QElidingLabel(TEXT)
    qtbot.addWidget(wdg)
    assert not wdg.wordWrap()
    assert 630 < wdg.sizeHint().width() < 635
    assert wdg._elidedText() == (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
        "eiusmod tempor incididunt ut labore et d…"
    )
    wdg.resize(QSize(200, 100))
    assert wdg.text() == TEXT
    assert wdg._elidedText() == "Lorem ipsum dolor sit amet, co…"
    wdg.setWordWrap(True)
    assert wdg.wordWrap()
    assert wdg.text() == TEXT
    assert wdg._elidedText() == (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do "
        "eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim ven iam, quis nostrud exercitation ullamco la…"
    )
    assert wdg.sizeHint() == QSize(200, 176)
    wdg.resize(wdg.sizeHint())
    assert wdg._elidedText() == TEXT


def test_shorter_eliding_label(qtbot):
    short = "asd a ads sd flksdf dsf lksfj sd lsdjf sd lsdfk sdlkfj s"
    wdg = QElidingLabel()
    qtbot.addWidget(wdg)
    wdg.setText(short)
    assert not wdg._elidedText().endswith(ELLIPSIS)
    wdg.resize(100, 20)
    assert wdg._elidedText().endswith(ELLIPSIS)
    wdg.setElideMode(Qt.TextElideMode.ElideLeft)
    assert wdg._elidedText().startswith(ELLIPSIS)
    assert wdg.elideMode() == Qt.TextElideMode.ElideLeft


def test_wrap_text():
    wrap = QElidingLabel.wrapText(TEXT, 200)
    assert isinstance(wrap, list)
    assert all(isinstance(x, str) for x in wrap)
    assert len(wrap) == 11
