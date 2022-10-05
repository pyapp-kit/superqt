from qtpy.QtWidgets import QTextEdit

from superqt.utils import CodeSyntaxHighlight


def test_code_highlight(qtbot):
    widget = QTextEdit()
    qtbot.addWidget(widget)
    code_highlight = CodeSyntaxHighlight(widget, "python", "default")
    assert code_highlight.background_color == "#f8f8f8"
    widget.setText("from argparse import ArgumentParser")


def test_code_highlight_by_name(qtbot):
    widget = QTextEdit()
    qtbot.addWidget(widget)
    code_highlight = CodeSyntaxHighlight(widget, "Python Traceback", "monokai")
    assert code_highlight.background_color == "#272822"
    widget.setText("from argparse import ArgumentParser")
