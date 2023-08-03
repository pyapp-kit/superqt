from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QResizeEvent

from superqt import QElidingLineEdit

TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do"
ELLIPSIS = "…"


def test_init_text_eliding_line_edit(qtbot):
    wdg = QElidingLineEdit(TEXT)
    qtbot.addWidget(wdg)
    oldsize = QSize(100, 20)
    wdg.resize(oldsize)
    assert wdg._elidedText().endswith(ELLIPSIS)
    newsize = QSize(500, 20)
    wdg.resize(newsize)
    wdg.resizeEvent(QResizeEvent(oldsize, newsize))  # for test coverage
    assert wdg._elidedText() == TEXT
    assert wdg.text() == TEXT


def test_set_text_eliding_line_edit(qtbot):
    wdg = QElidingLineEdit()
    qtbot.addWidget(wdg)
    wdg.resize(500, 20)
    wdg.setText(TEXT)
    assert not wdg._elidedText().endswith(ELLIPSIS)
    wdg.resize(100, 20)
    assert wdg._elidedText().endswith(ELLIPSIS)


def test_set_elide_mode_eliding_line_edit(qtbot):
    wdg = QElidingLineEdit()
    qtbot.addWidget(wdg)
    wdg.resize(500, 20)
    wdg.setText(TEXT)
    assert not wdg._elidedText().endswith(ELLIPSIS)
    wdg.resize(100, 20)
    # ellipses should be to the right
    assert wdg._elidedText().endswith(ELLIPSIS)

    # ellipses should be to the left
    wdg.setElideMode(Qt.TextElideMode.ElideLeft)
    assert wdg._elidedText().startswith(ELLIPSIS)
    assert wdg.elideMode() == Qt.TextElideMode.ElideLeft

    # no ellipses should be shown
    wdg.setElideMode(Qt.TextElideMode.ElideNone)
    assert ELLIPSIS not in wdg._elidedText()


def test_set_elipses_width_eliding_line_edit(qtbot):
    wdg = QElidingLineEdit()
    qtbot.addWidget(wdg)
    wdg.resize(500, 20)
    wdg.setText(TEXT)
    assert not wdg._elidedText().endswith(ELLIPSIS)
    wdg.setEllipsesWidth(int(wdg.width() / 2))
    assert wdg._elidedText().endswith(ELLIPSIS)
