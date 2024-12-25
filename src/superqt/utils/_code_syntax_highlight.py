from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import find_lexer_class, get_lexer_by_name
from pygments.util import ClassNotFound
from qtpy.QtGui import (
    QColor,
    QFont,
    QPalette,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import Literal, TypeAlias, TypedDict, Unpack

    import pygments.style
    from pygments.style import _StyleDict
    from pygments.token import _TokenType
    from qtpy.QtCore import QObject

    class SupportsDocumentAndPalette(QObject):
        def document(self) -> QTextDocument | None: ...
        def palette(self) -> QPalette: ...
        def setPalette(self, palette: QPalette) -> None: ...

    KnownStyle: TypeAlias = Literal[
        "abap",
        "algol",
        "algol_nu",
        "arduino",
        "autumn",
        "bw",
        "borland",
        "coffee",
        "colorful",
        "default",
        "dracula",
        "emacs",
        "friendly_grayscale",
        "friendly",
        "fruity",
        "github-dark",
        "gruvbox-dark",
        "gruvbox-light",
        "igor",
        "inkpot",
        "lightbulb",
        "lilypond",
        "lovelace",
        "manni",
        "material",
        "monokai",
        "murphy",
        "native",
        "nord-darker",
        "nord",
        "one-dark",
        "paraiso-dark",
        "paraiso-light",
        "pastie",
        "perldoc",
        "rainbow_dash",
        "rrt",
        "sas",
        "solarized-dark",
        "solarized-light",
        "staroffice",
        "stata-dark",
        "stata-light",
        "tango",
        "trac",
        "vim",
        "vs",
        "xcode",
        "zenburn",
    ]

    class FormatterKwargs(TypedDict, total=False):
        style: KnownStyle | str
        full: bool
        title: str
        encoding: str
        outencoding: str


MONO_FAMILIES = [
    "Menlo",
    "Courier New",
    "Courier",
    "Monaco",
    "Consolas",
    "Andale Mono",
    "Source Code Pro",
    "Ubuntu Mono",
    "monospace",
]


# inspired by  https://github.com/Vector35/snippets/blob/master/QCodeEditor.py
# (MIT license) and
# https://pygments.org/docs/formatterdevelopment/#html-3-2-formatter
def get_text_char_format(style: _StyleDict) -> QTextCharFormat:
    """Return a QTextCharFormat object based on the given Pygments `_StyleDict`.

    style will likely have these keys:
    - color: str | None
    - bold: bool
    - italic: bool
    - underline: bool
    - bgcolor: str | None
    - border: str | None
    - roman: bool | None
    - sans: bool | None
    - mono: bool | None
    - ansicolor: str | None
    - bgansicolor: str | None
    """
    text_char_format = QTextCharFormat()
    if style.get("mono"):
        text_char_format.setFontFamilies(MONO_FAMILIES)
    if color := style.get("color"):
        text_char_format.setForeground(QColor(f"#{color}"))
    if bgcolor := style.get("bgcolor"):
        text_char_format.setBackground(QColor(f"#{bgcolor}"))
    if style.get("bold"):
        text_char_format.setFontWeight(QFont.Weight.Bold)
    if style.get("italic"):
        text_char_format.setFontItalic(True)
    if style.get("underline"):
        text_char_format.setFontUnderline(True)
    # if style.get("border"):
    # ...
    return text_char_format


class QFormatter(Formatter):
    def __init__(self, **kwargs: Unpack[FormatterKwargs]) -> None:
        super().__init__(**kwargs)
        self.data: list[QTextCharFormat] = []
        style = cast("pygments.style.StyleMeta", self.style)
        self._style: Mapping[_TokenType, QTextCharFormat]
        self._style = {token: get_text_char_format(style) for token, style in style}

    def format(
        self, tokensource: Sequence[tuple[_TokenType, str]], outfile: Any
    ) -> None:
        """Format the given token stream.

        When Qt calls the highlightBlock method on a `CodeSyntaxHighlight` object,
        `highlight(text, self.lexer, self.formatter)`, which trigger pygments to call
        this method.

        Normally, this method puts output into `outfile`, but in Qt we do not produce
        string output; instead we collect QTextCharFormat objects in `self.data`, which
        can be used to apply formatting in the `highlightBlock` method that triggered
        this method.
        """
        self.data = []
        null = QTextCharFormat()
        for token, value in tokensource:
            # using get method to workaround not defined style for plain token
            # https://github.com/pygments/pygments/issues/2149
            self.data.extend([self._style.get(token, null)] * len(value))


class CodeSyntaxHighlight(QSyntaxHighlighter):
    """A syntax highlighter for code using Pygments.

    Parameters
    ----------
    parent : QTextDocument | QObject | None
        The parent object. Usually a QTextDocument.  To use this class with a
        QTextArea, pass in `text_area.document()`.
    lang : str
        The language of the code to highlight. This should be a string that
        Pygments recognizes, e.g. 'python', 'pytb', 'cpp', 'java', etc.
    theme : KnownStyle | str
        The name of the Pygments style to use. For a complete list of available
        styles, use `pygments.styles.get_all_styles()`.

    Examples
    --------
    ```python
    from qtpy.QtWidgets import QTextEdit
    from superqt.utils import CodeSyntaxHighlight

    text_area = QTextEdit()
    highlighter = CodeSyntaxHighlight(text_area.document(), "python", "monokai")

    # then manually apply the background color to the text area.
    palette = text_area.palette()
    bgrd_color = QColor(self._highlight.background_color)
    palette.setColor(QPalette.ColorRole.Base, bgrd_color)
    text_area.setPalette(palette)
    ```
    """

    def __init__(
        self,
        parent: SupportsDocumentAndPalette | QTextDocument | QObject | None,
        lang: str,
        theme: KnownStyle | str = "default",
    ) -> None:
        self._doc_parent: SupportsDocumentAndPalette | None = None
        if (
            parent
            and not isinstance(parent, QTextDocument)
            and hasattr(parent, "document")
            and callable(parent.document)
            and isinstance(doc := parent.document(), QTextDocument)
        ):
            if hasattr(parent, "palette") and hasattr(parent, "setPalette"):
                self._doc_parent = cast("SupportsDocumentAndPalette", parent)
            parent = doc

        super().__init__(parent)
        self.setLanguage(lang)
        self.setTheme(theme)

    def setTheme(self, theme: KnownStyle | str) -> None:
        """Set the theme for the syntax highlighting.

        This should be a string that Pygments recognizes, e.g. 'monokai', 'solarized'.
        Use `pygments.styles.get_all_styles()` to see a list of available styles.
        """
        self.formatter = QFormatter(style=theme)
        if self._doc_parent is not None:
            palette = self._doc_parent.palette()
            bgrd = QColor(self.background_color)
            palette.setColor(QPalette.ColorRole.Base, bgrd)
            self._doc_parent.setPalette(palette)

        self.rehighlight()

    def setLanguage(self, lang: str) -> None:
        """Set the language for the syntax highlighting.

        This should be a string that Pygments recognizes, e.g. 'python', 'pytb', 'cpp',
        'java', etc.
        """
        try:
            self.lexer = get_lexer_by_name(lang)
        except ClassNotFound as e:
            if cls := find_lexer_class(lang):
                self.lexer = cls()
            else:
                raise ValueError(f"Could not find lexer for language {lang!r}.") from e

    @property
    def background_color(self) -> str:
        style = cast("pygments.style.StyleMeta", self.formatter.style)
        return style.background_color

    def highlightBlock(self, text: str | None) -> None:
        # dirty, dirty hack
        # The core problem is that pygments by default use string streams,
        # that will not handle QTextCharFormat, so we need use `data` property to
        # work around this.
        if text:
            highlight(text, self.lexer, self.formatter)
            for i in range(len(text)):
                self.setFormat(i, 1, self.formatter.data[i])
