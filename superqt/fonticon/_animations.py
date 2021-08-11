from abc import ABC, abstractmethod

from superqt.qtcompat.QtCore import QRect, QRectF, QTimer
from superqt.qtcompat.QtGui import QIcon, QPainter


class Animation(ABC):
    def __init__(self, parent_widget, interval=8, step=1):
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
    def animate(self, painter: "QPainter", rect: QRect, mode: QIcon.Mode):
        ...


class spin(Animation):
    def animate(self, painter: "QPainter", rect: QRect, mode: QIcon.Mode):
        if self.timer.isActive() and mode == QIcon.Mode.Disabled:
            self.timer.stop()
        elif mode != QIcon.Mode.Disabled:
            self.timer.start()
        self._tick(painter, rect)

    def _tick(self, painter, rect):
        mid = QRectF(rect).center()
        painter.translate(mid)
        painter.rotate(self._angle % 360)
        painter.translate(-mid)


class step(spin):
    def __init__(self, parent_widget):
        super().__init__(parent_widget, interval=200, step=45)
