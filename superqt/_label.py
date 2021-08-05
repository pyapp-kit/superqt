from .qtcompat.QtCore import QPoint, QRect, QSize, Qt
from .qtcompat.QtGui import QFontMetrics, QPainter, QTextLayout
from .qtcompat.QtWidgets import QLabel


class QElidingLabel(QLabel):
    """A single-line eliding QLabel."""

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
        super().setText(self._shortText())

    def setText(self, txt):
        self._text = txt
        super().setText(self._shortText())

    def fullText(self) -> str:
        return self._text

    def resizeEvent(self, rEvent):
        super().setText(self._shortText(rEvent.size().width()))
        rEvent.accept()

    def _shortText(self, width=None):
        width = width or self.width()
        self.fm = QFontMetrics(self.font())
        return self.fm.elidedText(self._text, self._elide_mode, width)


class QMultilineElidingLabel(QLabel):
    """A multiline QLabel-like widget that elides the last line.

    Behaves like a multiline QLabel, but will fill the available vertical space
    set by the parent, and elide the last line of text (i.e. cut off with an
    ellipses.)

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget, by default None
    text : str, optional
        The text to show in the label, by default ''
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if args and isinstance(args[0], str):
            self.setText(args[0])

    def text(self) -> str:
        return self._text

    def setText(self, text=None):
        if text is not None:
            self._text = text
        self.update()
        self.adjustSize()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        font_metrics = painter.fontMetrics()
        text_layout = QTextLayout(self._text, painter.font())
        text_layout.beginLayout()

        y = 0
        while True:
            line = text_layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(self.width())
            nextLineY = y + font_metrics.lineSpacing()
            if self.height() >= nextLineY + font_metrics.lineSpacing():
                line.draw(painter, QPoint(0, y))
                y = nextLineY
            else:
                lastLine = self._text[line.textStart() :]
                elidedLastLine = font_metrics.elidedText(
                    lastLine, Qt.ElideRight, self.width()
                )
                painter.drawText(QPoint(0, y + font_metrics.ascent()), elidedLastLine)
                line = text_layout.createLine()
                break
        text_layout.endLayout()

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        r = font_metrics.boundingRect(
            QRect(QPoint(0, 0), self.size()),
            Qt.TextWordWrap | Qt.ElideRight,
            self._text,
        )
        return QSize(self.width(), r.height())
