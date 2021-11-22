"""A collapsible widget to hide and unhide child widgets"""
from typing import Optional

from ..qtcompat.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QMargins,
    QPropertyAnimation,
    Qt,
)
from ..qtcompat.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget


class QCollapsible(QFrame):
    """A collapsible widget to hide and unhide child widgets.

    Based on https://stackoverflow.com/a/68141638
    """

    _EXPANDED = "▼  "
    _COLLAPSED = "▲  "

    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._locked = False

        self._toggle_btn = QPushButton(self._COLLAPSED + title)
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setStyleSheet("text-align: left; background: transparent;")
        self._toggle_btn.toggled.connect(self._toggle)

        # frame layout
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addWidget(self._toggle_btn)

        # Create animators
        self._animation = QPropertyAnimation(self)
        self._animation.setPropertyName(b"maximumHeight")
        self._animation.setStartValue(0)
        self.setDuration(300)
        self.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # default content widget
        _content = QWidget()
        _content.setLayout(QVBoxLayout())
        _content.setMaximumHeight(0)
        _content.layout().setContentsMargins(QMargins(5, 0, 0, 0))
        self.setContent(_content)

    def setText(self, text: str):
        """Set the text of the toggle button."""
        current = self._toggle_btn.text()[: len(self._EXPANDED)]
        self._toggle_btn.setText(current + text)

    def text(self) -> str:
        """Return the text of the toggle button."""
        return self._toggle_btn.text()[len(self._EXPANDED) :]

    def setContent(self, content: QWidget):
        """Replace central widget (the widget that gets expanded/collapsed)."""
        self._content = content
        self.layout().addWidget(self._content)
        self._animation.setTargetObject(content)

    def content(self) -> QWidget:
        """Return the current content widget."""
        return self._content

    def setDuration(self, msecs: int):
        """Set duration of the collapse/expand animation."""
        self._animation.setDuration(msecs)

    def setEasingCurve(self, easing: QEasingCurve):
        """Set the easing curve for the collapse/expand animation"""
        self._animation.setEasingCurve(easing)

    def addWidget(self, widget: QWidget):
        """Add a widget to the central content widget's layout."""
        self._content.layout().addWidget(widget)

    def removeWidget(self, widget: QWidget):
        """Remove widget from the central content widget's layout."""
        self._content.layout().removeWidget(widget)

    def expand(self, animate: bool = True):
        """Expand (show) the collapsible section"""
        self._expand_collapse(QAbstractAnimation.Direction.Forward, animate)

    def collapse(self, animate: bool = True):
        """Collapse (hide) the collapsible section"""
        self._expand_collapse(QAbstractAnimation.Direction.Backward, animate)

    def isExpanded(self) -> bool:
        """Return whether the collapsible section is visible"""
        return self._toggle_btn.isChecked()

    def setLocked(self, locked: bool = True):
        """Set whether collapse/expand is disabled"""
        self._locked = locked
        self._toggle_btn.setCheckable(not locked)

    def locked(self) -> bool:
        """Return True if collapse/expand is disabled"""
        return self._locked

    def _expand_collapse(
        self, direction: QAbstractAnimation.Direction, animate: bool = True
    ):
        if self._locked:
            return

        forward = direction == QAbstractAnimation.Direction.Forward
        text = self._EXPANDED if forward else self._COLLAPSED

        self._toggle_btn.setChecked(forward)
        self._toggle_btn.setText(text + self._toggle_btn.text()[len(self._EXPANDED) :])

        _content_height = self._content.sizeHint().height() + 10
        if animate:
            self._animation.setDirection(direction)
            self._animation.setEndValue(_content_height)
            self._animation.start()
        else:
            self._content.setMaximumHeight(_content_height if forward else 0)

    def _toggle(self):
        self.expand() if self.isExpanded() else self.collapse()
