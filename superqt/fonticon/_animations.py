from abc import ABC, abstractmethod

from superqt.qtcompat.QtCore import QRect, QRectF, QTimer
from superqt.qtcompat.QtGui import QPainter


class Animation(ABC):
    def __init__(self, parent_widget, interval=10, step=1):
        self.parent_widget = parent_widget
        self.timer = QTimer(self.parent_widget)
        self.timer.timeout.connect(self._update)
        self.timer.setInterval(interval)
        self._angle = 0
        self._step = step

    def _update(self):
        if self.timer.isActive():
            self._angle += self._step
            self.parent_widget.update()

    @abstractmethod
    def animate(self, painter: "QPainter", rect: QRect):
        ...


class spin(Animation):
    def animate(self, painter: "QPainter", rect: QRect):
        if not self.timer.isActive():
            self.timer.start()
        mid = QRectF(rect).center()
        painter.translate(mid)
        painter.rotate(self._angle % 360)
        painter.translate(-mid)


class pulse(spin):
    def __init__(self, parent_widget):
        super().__init__(parent_widget, interval=200, step=45)