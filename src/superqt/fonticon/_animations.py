from abc import ABC, abstractmethod

from qtpy.QtCore import QRectF, QTimer
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QWidget


class Animation(ABC):
    def __init__(self, parent_widget: QWidget, interval: int = 10, step: int = 1):
        self.parent_widget = parent_widget
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)  # type: ignore
        self.timer.setInterval(interval)
        self._angle = 0
        self._step = step

    def _update(self):
        if self.timer.isActive():
            self._angle += self._step
            self.parent_widget.update()

    @abstractmethod
    def animate(self, painter: QPainter):
        """Setup and start the timer for the animation."""


class spin(Animation):
    def animate(self, painter: QPainter):
        if not self.timer.isActive():
            self.timer.start()

        mid = QRectF(painter.viewport()).center()
        painter.translate(mid)
        painter.rotate(self._angle % 360)
        painter.translate(-mid)


class pulse(spin):
    def __init__(self, parent_widget: QWidget = None):
        super().__init__(parent_widget, interval=200, step=45)
