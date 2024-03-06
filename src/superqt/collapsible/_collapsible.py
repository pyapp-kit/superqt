"""A collapsible widget to hide and unhide child widgets."""

from __future__ import annotations

from qtpy.QtCore import (
    QEasingCurve,
    QEvent,
    QMargins,
    QObject,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
)
from qtpy.QtGui import QIcon, QPainter, QPalette, QPixmap
from qtpy.QtWidgets import QFrame, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class QCollapsible(QFrame):
    """A collapsible widget to hide and unhide child widgets.

    A signal is emitted when the widget is expanded (True) or collapsed (False).

    Based on https://stackoverflow.com/a/68141638
    """

    toggled = Signal(bool)

    def __init__(
        self,
        title: str = "",
        parent: QWidget | None = None,
        expandedIcon: QIcon | str | None = "▼",
        collapsedIcon: QIcon | str | None = "▲",
    ):
        super().__init__(parent)
        self._locked = False
        self._is_animating = False
        self._text = title

        self._toggle_btn = QPushButton(title)
        self._toggle_btn.setCheckable(True)
        self.setCollapsedIcon(icon=collapsedIcon)
        self.setExpandedIcon(icon=expandedIcon)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self._toggle_btn.setStyleSheet("text-align: left; border: none; outline: none;")
        self._toggle_btn.toggled.connect(self._toggle)

        # frame layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._toggle_btn)

        # Create animators
        self._animation = QPropertyAnimation(self)
        self._animation.setPropertyName(b"maximumHeight")
        self._animation.setStartValue(0)
        self._animation.finished.connect(self._on_animation_done)
        self.setDuration(300)
        self.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # default content widget
        _content = QWidget()
        _content.setLayout(QVBoxLayout())
        _content.setMaximumHeight(0)
        _content.layout().setContentsMargins(QMargins(5, 0, 0, 0))
        self.setContent(_content)

    def toggleButton(self) -> QPushButton:
        """Return the toggle button."""
        return self._toggle_btn

    def setText(self, text: str) -> None:
        """Set the text of the toggle button."""
        self._toggle_btn.setText(text)

    def text(self) -> str:
        """Return the text of the toggle button."""
        return self._toggle_btn.text()

    def setContent(self, content: QWidget) -> None:
        """Replace central widget (the widget that gets expanded/collapsed)."""
        self._content = content
        self.layout().addWidget(self._content)
        self._animation.setTargetObject(content)

    def content(self) -> QWidget:
        """Return the current content widget."""
        return self._content

    def _convert_string_to_icon(self, symbol: str) -> QIcon:
        """Create a QIcon from a string."""
        size = self._toggle_btn.font().pointSize()
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        color = self._toggle_btn.palette().color(QPalette.ColorRole.WindowText)
        painter.setPen(color)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, symbol)
        painter.end()
        return QIcon(pixmap)

    def expandedIcon(self) -> QIcon:
        """Returns the icon used when the widget is expanded."""
        return self._expanded_icon

    def setExpandedIcon(self, icon: QIcon | str | None = None) -> None:
        """Set the icon on the toggle button when the widget is expanded."""
        if icon and isinstance(icon, QIcon):
            self._expanded_icon = icon
        elif icon and isinstance(icon, str):
            self._expanded_icon = self._convert_string_to_icon(icon)

        if self.isExpanded():
            self._toggle_btn.setIcon(self._expanded_icon)

    def collapsedIcon(self) -> QIcon:
        """Returns the icon used when the widget is collapsed."""
        return self._collapsed_icon

    def setCollapsedIcon(self, icon: QIcon | str | None = None) -> None:
        """Set the icon on the toggle button when the widget is collapsed."""
        if icon and isinstance(icon, QIcon):
            self._collapsed_icon = icon
        elif icon and isinstance(icon, str):
            self._collapsed_icon = self._convert_string_to_icon(icon)

        if not self.isExpanded():
            self._toggle_btn.setIcon(self._collapsed_icon)

    def setDuration(self, msecs: int) -> None:
        """Set duration of the collapse/expand animation."""
        self._animation.setDuration(msecs)

    def setEasingCurve(self, easing: QEasingCurve | QEasingCurve.Type) -> None:
        """Set the easing curve for the collapse/expand animation."""
        self._animation.setEasingCurve(easing)

    def addWidget(self, widget: QWidget) -> None:
        """Add a widget to the central content widget's layout."""
        widget.installEventFilter(self)
        self._content.layout().addWidget(widget)

    def removeWidget(self, widget: QWidget) -> None:
        """Remove widget from the central content widget's layout."""
        self._content.layout().removeWidget(widget)
        widget.removeEventFilter(self)

    def expand(self, animate: bool = True) -> None:
        """Expand (show) the collapsible section."""
        self._expand_collapse(QPropertyAnimation.Direction.Forward, animate)

    def collapse(self, animate: bool = True) -> None:
        """Collapse (hide) the collapsible section."""
        self._expand_collapse(QPropertyAnimation.Direction.Backward, animate)

    def isExpanded(self) -> bool:
        """Return whether the collapsible section is visible."""
        return self._toggle_btn.isChecked()

    def setLocked(self, locked: bool = True) -> None:
        """Set whether collapse/expand is disabled."""
        self._locked = locked
        self._toggle_btn.setCheckable(not locked)

    def locked(self) -> bool:
        """Return True if collapse/expand is disabled."""
        return self._locked

    def _expand_collapse(
        self,
        direction: QPropertyAnimation.Direction,
        animate: bool = True,
        emit: bool = True,
    ) -> None:
        """Set values for the widget based on whether it is expanding or collapsing.

        An emit flag is included so that the toggle signal is only called once (it
        was being emitted a few times via eventFilter when the widget was expanding
        previously).
        """
        if self._locked:
            return

        forward = direction == QPropertyAnimation.Direction.Forward
        icon = self._expanded_icon if forward else self._collapsed_icon
        self._toggle_btn.setIcon(icon)
        self._toggle_btn.setChecked(forward)

        _content_height = self._content.sizeHint().height() + 10
        if animate:
            self._animation.setDirection(direction)
            self._animation.setEndValue(_content_height)
            self._is_animating = True
            self._animation.start()
        else:
            self._content.setMaximumHeight(_content_height if forward else 0)
        if emit:
            self.toggled.emit(direction == QPropertyAnimation.Direction.Forward)

    def _toggle(self) -> None:
        self.expand() if self.isExpanded() else self.collapse()

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        """If a child widget resizes, we need to update our expanded height."""
        if (
            a1.type() == QEvent.Type.Resize
            and self.isExpanded()
            and not self._is_animating
        ):
            self._expand_collapse(
                QPropertyAnimation.Direction.Forward, animate=False, emit=False
            )
        return False

    def _on_animation_done(self) -> None:
        self._is_animating = False
