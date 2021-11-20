"""A collapsible widget to hide and unhide child widgets"""
from typing import Optional

from ..qtcompat.QtCore import QAbstractAnimation, QEasingCurve, QPropertyAnimation, Qt
from ..qtcompat.QtWidgets import QFrame, QPushButton, QVBoxLayout, QWidget


class QCollapsible(QFrame):
    """
    A collapsible widget to hide and unhide child widgets.

    Based on https://stackoverflow.com/a/68141638
    """

    _EXPANDED = "▼  "
    _COLLAPSED = "▲  "

    def __init__(
        self, title: str = "", parent: Optional[QWidget] = None, flags=Qt.WindowFlags()
    ):
        super().__init__(parent, flags)
        self._locked = False

        self._toggle_btn = QPushButton(self._COLLAPSED + title)
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setChecked(False)
        self._toggle_btn.setStyleSheet("text-align: left; background: transparent;")
        self._toggle_btn.clicked.connect(self._toggle)

        # frame layout
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
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
        self.setContent(_content)

    def setText(self, text: str):
        current = self._toggle_btn.text()[: len(self._EXPANDED)]
        self._toggle_btn.setText(current + text)

    def setContent(self, content: QWidget):
        self._content = content
        self.layout().addWidget(self._content)
        self._animation.setTargetObject(content)

    def content(self) -> QWidget:
        return self._content

    def setDuration(self, msecs: int):
        self._animation.setDuration(msecs)

    def setEasingCurve(self, easing: QEasingCurve):
        self._animation.setEasingCurve(easing)

    def addWidget(self, widget: QWidget):
        self._content.layout().addWidget(widget)

    def removeWidget(self, widget: QWidget):
        self._content.layout().removeWidget(widget)

    def expand(self, animate: bool = True):
        if self._locked:
            return

        self._toggle_btn.setChecked(True)
        self._toggle_btn.setText(
            self._EXPANDED + self._toggle_btn.text()[len(self._COLLAPSED) :]
        )
        if animate:
            self._animate(QAbstractAnimation.Direction.Forward)
        else:
            self._content.setMaximumHeight(self._content.sizeHint().height() + 10)

    def collapse(self, animate: bool = True):
        if self._locked:
            return
        self._toggle_btn.setChecked(False)
        self._toggle_btn.setText(
            self._COLLAPSED + self._toggle_btn.text()[len(self._EXPANDED) :]
        )
        if animate:
            self._animate(QAbstractAnimation.Direction.Backward)
        else:
            self._content.setMaximumHeight(0)

    def expanded(self):
        return self._toggle_btn.isChecked()

    def _animate(self, direction: QAbstractAnimation.Direction):
        self._animation.setDirection(direction)
        self._animation.setEndValue(self._content.sizeHint().height() + 10)
        self._animation.start()

    def _toggle(self):
        if self._locked is True:
            self._toggle_btn.setChecked(not self._toggle_btn.isChecked)
        self.expand() if self._toggle_btn.isChecked() else self.collapse()

    def setLocked(self, locked: bool = True):
        self._locked = locked

    def locked(self) -> bool:
        return self._locked
