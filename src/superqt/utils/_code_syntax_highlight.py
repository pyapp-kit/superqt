from itertools import takewhile

from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import find_lexer_class, get_lexer_by_name
from pygments.util import ClassNotFound
from qtpy import QtGui

# inspired by  https://github.com/Vector35/snippets/blob/master/QCodeEditor.py
# (MIT license) and
# https://pygments.org/docs/formatterdevelopment/#html-3-2-formatter


def get_text_char_format(style):
    text_char_format = QtGui.QTextCharFormat()
    if hasattr(text_char_format, "setFontFamilies"):
        text_char_format.setFontFamilies(["monospace"])
    else:
        text_char_format.setFontFamily("monospace")
    if style.get("color"):
        text_char_format.setForeground(QtGui.QColor(f"#{style['color']}"))

    if style.get("bgcolor"):
        text_char_format.setBackground(QtGui.QColor(style["bgcolor"]))

    if style.get("bold"):
        text_char_format.setFontWeight(QtGui.QFont.Bold)
    if style.get("italic"):
        text_char_format.setFontItalic(True)
    if style.get("underline"):
        text_char_format.setFontUnderline(True)

    # TODO find if it is possible to support border style.

    return text_char_format


class QFormatter(Formatter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        self._style = {name: get_text_char_format(style) for name, style in self.style}

    def format(self, tokensource, outfile):
        """Format the given token stream.

        `outfile` is argument from parent class, but
        in Qt we do not produce string output, but QTextCharFormat, so it needs to be
        collected using `self.data`.
        """
        self.data = []

        for token, value in tokensource:
            self.data.extend([self._style[token]] * len(value))


class CodeSyntaxHighlight(QtGui.QSyntaxHighlighter):
    def __init__(self, parent, lang, theme):
        super().__init__(parent)
        self.formatter = QFormatter(style=theme)
        try:
            self.lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            self.lexer = find_lexer_class(lang)()

    @property
    def background_color(self):
        return self.formatter.style.background_color

    def highlightBlock(self, text):
        cb = self.currentBlock()
        p = cb.position()
        text_ = self.document().toPlainText() + "\n"
        highlight(text_, self.lexer, self.formatter)

        enters = sum(1 for _ in takewhile(lambda x: x == "\n", text_))
        # pygments lexer ignore leading empty lines, so we need to do correction
        # here calculating the number of empty lines.

        # dirty, dirty hack
        # The core problem is that pygemnts by default use string streams,
        # that will not handle QTextCharFormat, so wee need use `data` property to
        # work around this.
        for i in range(len(text)):
            try:
                self.setFormat(i, 1, self.formatter.data[p + i - enters])
            except IndexError:  # pragma: no cover
                pass
