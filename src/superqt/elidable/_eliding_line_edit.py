from qtpy.QtCore import Qt
from qtpy.QtGui import QFocusEvent, QResizeEvent
from qtpy.QtWidgets import QLineEdit

from ._eliding import _GenericEliding


class QElidingLineEdit(_GenericEliding, QLineEdit):
    """A QLineEdit variant that will elide text (could add '…') to fit width.

    QElidingLineEdit()
    QElidingLineEdit(parent: Optional[QWidget])
    QElidingLineEdit(text: str, parent: Optional[QWidget] = None)

    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if args and isinstance(args[0], str):
            self.setText(args[0])
        # The `textEdited` signal doesn't trigger the `textChanged` signal if
        # text is changed with `setText`, so we connect to `textEdited` to only
        # update _text when text is being edited by the user graphically.
        self.textEdited.connect(self._update_text)

    # Reimplemented _GenericEliding methods

    def setElideMode(self, mode: Qt.TextElideMode) -> None:
        """Set the elide mode to a Qt.TextElideMode.

        The text shown is updated to the elided version only if the widget is not
        focused.
        """
        super().setElideMode(mode)
        if not self.hasFocus():
            super().setText(self._elidedText())

    def setEllipsesWidth(self, width: int) -> None:
        """A width value to take into account ellipses width when eliding text.

        The value is deducted from the widget width when computing the elided version
        of the text. The text shown is updated to the elided version only if the widget
        is not focused.
        """
        super().setEllipsesWidth(width)
        if not self.hasFocus():
            super().setText(self._elidedText())

    # Reimplemented QT methods

    def text(self) -> str:
        """Return the label's text being shown.

        If no text has been set this will return an empty string.
        """
        return self._text

    def setText(self, text) -> None:
        """Set the line edit's text.

        Setting the text clears any previous content.
        NOTE: we set the QLineEdit private text to the elided version
        """
        self._text = text
        if not self.hasFocus():
            super().setText(self._elidedText())

    def focusInEvent(self, event: QFocusEvent) -> None:
        """Set the full text when the widget is focused."""
        super().setText(self._text)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Set an elided version of the text (if needed) when the focus is out."""
        super().setText(self._elidedText())
        super().focusOutEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Update elided text being shown when the widget is resized."""
        if not self.hasFocus():
            super().setText(self._elidedText())
        super().resizeEvent(event)

    # private implementation methods

    def _update_text(self, text: str) -> None:
        """Update only the actual text of the widget.

        The actual text is the text the widget has without eliding.
        """
        self._text = text
