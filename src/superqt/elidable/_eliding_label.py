from qtpy.QtCore import QPoint, QRect, QSize, Qt
from qtpy.QtGui import QFontMetrics, QResizeEvent
from qtpy.QtWidgets import QLabel

from ._eliding import _GenericEliding


class QElidingLabel(_GenericEliding, QLabel):
    """
    A QLabel variant that will elide text (could add '…') to fit width.

    QElidingLabel()
    QElidingLabel(parent: Optional[QWidget], f: Qt.WindowFlags = ...)
    QElidingLabel(text: str, parent: Optional[QWidget] = None, f: Qt.WindowFlags = ...)

    For a multiline eliding label, use `setWordWrap(True)`.  In this case, text
    will wrap to fit the width, and only the last line will be elided.
    When `wordWrap()` is True, `sizeHint()` will return the size required to fit
    the full text.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if args and isinstance(args[0], str):
            self.setText(args[0])

    # Reimplemented _GenericEliding methods

    def setElideMode(self, mode: Qt.TextElideMode) -> None:
        """Set the elide mode to a Qt.TextElideMode."""
        super().setElideMode(mode)
        super().setText(self._elidedText())

    def setEllipsesWidth(self, width: int) -> None:
        """A width value to take into account ellipses width when eliding text.

        The value is deducted from the widget width when computing the elided version
        of the text.
        """
        super().setEllipsesWidth(width)
        super().setText(self._elidedText())

    # Reimplemented QT methods

    def text(self) -> str:
        """Return the label's text.

        If no text has been set this will return an empty string.
        """
        return self._text

    def setText(self, txt: str) -> None:
        """Set the label's text.

        Setting the text clears any previous content.
        NOTE: we set the QLabel private text to the elided version
        """
        self._text = txt
        super().setText(self._elidedText())

    def resizeEvent(self, event: QResizeEvent) -> None:
        event.accept()
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

    def minimumSizeHint(self) -> QSize:
        # The smallest that self._elidedText can be is just the ellipsis.
        fm = QFontMetrics(self.font())
        flags = int(self.alignment() | Qt.TextFlag.TextWordWrap)
        r = fm.boundingRect(QRect(QPoint(0, 0), self.size()), flags, "...")
        return QSize(r.width(), r.height())
