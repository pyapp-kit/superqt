from typing import List

from qtpy.QtCore import QPoint, QRect, QSize, Qt
from qtpy.QtGui import QFont, QFontMetrics, QResizeEvent, QTextLayout
from qtpy.QtWidgets import QLabel


class QElidingLabel(QLabel):
    """A QLabel variant that will elide text (add '…') to fit width.

    QElidingLabel()
    QElidingLabel(parent: Optional[QWidget], f: Qt.WindowFlags = ...)
    QElidingLabel(text: str, parent: Optional[QWidget] = None, f: Qt.WindowFlags = ...)

    For a multiline eliding label, use `setWordWrap(True)`.  In this case, text
    will wrap to fit the width, and only the last line will be elided.
    When `wordWrap()` is True, `sizeHint()` will return the size required to fit
    the full text.
    """

    def __init__(self, *args, **kwargs) -> None:
        self._elide_mode = Qt.TextElideMode.ElideRight
        super().__init__(*args, **kwargs)
        self.setText(args[0] if args and isinstance(args[0], str) else "")

    # New Public methods

    def elideMode(self) -> Qt.TextElideMode:
        """The current Qt.TextElideMode."""
        return self._elide_mode

    def setElideMode(self, mode: Qt.TextElideMode):
        """Set the elide mode to a Qt.TextElideMode."""
        self._elide_mode = Qt.TextElideMode(mode)
        super().setText(self._elidedText())

    @staticmethod
    def wrapText(text, width, font=None) -> List[str]:
        """Returns `text`, split as it would be wrapped for `width`, given `font`.

        Static method.
        """
        tl = QTextLayout(text, font or QFont())
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

    def text(self) -> str:
        """Return the label's text.

        If no text has been set this will return an empty string.
        """
        return self._text

    def setText(self, txt: str):
        """Set the label's text.

        Setting the text clears any previous content.
        NOTE: we set the QLabel private text to the elided version
        """
        self._text = txt
        super().setText(self._elidedText())

    def resizeEvent(self, ev: QResizeEvent) -> None:
        ev.accept()
        super().setText(self._elidedText())

    def setWordWrap(self, wrap: bool) -> None:
        super().setWordWrap(wrap)
        super().setText(self._elidedText())

    def sizeHint(self) -> QSize:
        if not self.wordWrap():
            return super().sizeHint()
        fm = QFontMetrics(self.font())
        flags = int(self.alignment() | Qt.TextFlag.TextWordWrap)
        r = fm.boundingRect(QRect(QPoint(0, 0), self.size()), flags, self._text)
        return QSize(self.width(), r.height())

    # private implementation methods

    def _elidedText(self) -> str:
        """Return `self._text` elided to `width`."""
        fm = QFontMetrics(self.font())
        # the 2 is a magic number that prevents the ellipses from going missing
        # in certain cases (?)
        width = self.width() - 2
        if not self.wordWrap():
            return fm.elidedText(self._text, self._elide_mode, width)

        # get number of lines we can fit without eliding
        nlines = self.height() // fm.height() - 1
        # get the last line (elided)
        text = self._wrappedText()
        last_line = fm.elidedText("".join(text[nlines:]), self._elide_mode, width)
        # join them
        return "".join(text[:nlines] + [last_line])

    def _wrappedText(self) -> List[str]:
        return QElidingLabel.wrapText(self._text, self.width(), self.font())
