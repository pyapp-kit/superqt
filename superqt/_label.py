from .qtcompat.QtCore import Qt
from .qtcompat.QtGui import QFontMetrics
from .qtcompat.QtWidgets import QLabel


class QElidingLabel(QLabel):
    """A single-line eliding QLabel."""

    ELIDE_STRING = "…"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._elide_mode = Qt.ElideRight  # type: ignore
        self._text = ""
        if args and isinstance(args[0], str):
            self._text = args[0]

    def elideMode(self) -> Qt.TextElideMode:
        return self._elide_mode

    def setElideMode(self, mode: Qt.TextElideMode):
        self._elide_mode = Qt.TextElideMode(mode)
        super().setText(self._elidedText())

    def setText(self, txt):
        self._text = txt
        super().setText(self._elidedText())

    def fullText(self) -> str:
        return self._text

    def resizeEvent(self, rEvent):
        super().setText(self._elidedText(rEvent.size().width()))
        rEvent.accept()

    def setWordWrap(self, wrap: bool) -> None:
        super().setWordWrap(wrap)
        super().setText(self._elidedText())

    def _elidedText(self, width=None):
        fm = QFontMetrics(self.font())
        if not self.wordWrap():
            width = width or self.width()
            return fm.elidedText(self._text, self._elide_mode, width)

        flags = self.alignment() | Qt.TextWordWrap
        n = 0
        text = self._text
        # looping makes for quick code, but slow execution.
        while fm.boundingRect(self.rect(), flags, text).y() < 0 and n < 100:
            text = text[:-8] + self.ELIDE_STRING
            n += 1
        return text
