from typing import List, Optional, overload

from superqt.qtcompat.QtCore import QPoint, QRect, QSize, Qt
from superqt.qtcompat.QtGui import QFont, QFontMetrics, QResizeEvent, QTextLayout
from superqt.qtcompat.QtWidgets import QLabel, QWidget


class QElidingLabel(QLabel):
    """A QLabel variant that will elide text (add '…') to fit width.

    QElidingLabel(parent: Optional[QWidget] = None, f: Qt.WindowFlags = ...)
    QElidingLabel(text: str, parent: Optional[QWidget] = None, f: Qt.WindowFlags = ...)

    For a multiline eliding label, use `setWordWrap(True)`.  In this case, text
    will wrap to fit the width, and only the last line will be elided.
    When `wordWrap()` is True, `sizeHint()` will return the size required to fit the
    full text.
    """

    ELIDE_STRING = "…"

    # fmt: off
    @overload
    def __init__(self, parent: Optional[QWidget] = ..., f: Qt.WindowFlags = ...) -> None: ...  # noqa
    @overload
    def __init__(self, text: str, parent: Optional[QWidget] = ..., f: Qt.WindowFlags = ...) -> None: ...  # noqa
    # fmt: on

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._elide_mode = Qt.TextElideMode.ElideRight
        self._text = ""
        if args and isinstance(args[0], str):
            self._text = args[0]

    # New Public methods

    def elideMode(self) -> Qt.TextElideMode:
        """The current Qt.TextElideMode."""
        return self._elide_mode

    def setElideMode(self, mode: Qt.TextElideMode):
        """Set the elide mode to a Qt.TextElideMode."""
        self._elide_mode = Qt.TextElideMode(mode)  # type: ignore
        super().setText(self._elidedText())

    def fullText(self) -> str:
        """Return the full un-elided text."""
        return self._text

    @staticmethod
    def wrapText(text, width, font=QFont()) -> List[str]:
        """Returns `text`, split as it would be wrapped for `width`, given `font`.

        Static method.
        """
        tl = QTextLayout(text, font)
        tl.beginLayout()
        lines = []
        while True:
            ln = tl.createLine()
            if not ln.isValid():
                break
            ln.setLineWidth(width)
            start = ln.textStart()
            lines.append(text[start : start + ln.textLength()])
        tl.endLayout()
        return lines

    # Reimplemented QT methods

    def setText(self, txt):
        self._text = txt
        super().setText(self._elidedText())

    def resizeEvent(self, rEvent: QResizeEvent):
        super().setText(self._elidedText(rEvent.size().width()))
        rEvent.accept()

    def setWordWrap(self, wrap: bool) -> None:
        super().setWordWrap(wrap)
        super().setText(self._elidedText())

    def sizeHint(self):
        if not self.wordWrap():
            return super().sizeHint()
        fm = QFontMetrics(self.font())
        flags = self.alignment() | Qt.Text.TextWordWrap
        r = fm.boundingRect(QRect(QPoint(0, 0), self.size()), flags, self._text)
        return QSize(self.width(), r.height())

    # private implementation methods

    def _elidedText(self, width=None):
        """Return `self._text` elided to `width`"""
        fm = QFontMetrics(self.font())
        # the 2 is a magic number that prevents the ellipses from going missing
        # in certain cases (?)
        width = (width or self.width()) - 2
        if not self.wordWrap():
            return fm.elidedText(self._text, self._elide_mode, width)

        # get number of lines we can fit without eliding
        nlines = self.height() // fm.height() - 1
        # get the last line (elided)
        text = self._wrappedText()
        last_line = fm.elidedText("".join(text[nlines:]), self._elide_mode, width)
        # join them
        return "".join(text[:nlines] + [last_line])

    def _wrappedText(self):
        return QElidingLabel.wrapText(self._text, self.width(), self.font())
