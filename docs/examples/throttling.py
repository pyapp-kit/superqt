"""A slider's valueChanged, connected directly, throttled, and debounced.

Drag the slider: each lane of the timeline draws a tick for each call (newest on
the right), and shows the value that the last call received. (Inspired by
examples/throttler_demo.py, which is adapted from KDAB's KDToolBox.)
"""

import time
from collections import deque

from qtpy.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from qtpy.QtGui import QColor, QPainter, QPen
from qtpy.QtWidgets import QApplication, QSlider, QVBoxLayout, QWidget

from superqt.utils import qdebounced, qthrottled

SPEED = 100  # pixels per second
LABEL_WIDTH = 170


class Timeline(QWidget):
    """Lanes of ticks that scroll to the left, one lane per kind of call."""

    def __init__(self, lanes: dict[str, str]) -> None:
        super().__init__()
        self._colors = lanes  # lane name -> tick color
        self._ticks = {name: deque() for name in lanes}
        self._values = dict.fromkeys(lanes, "")
        self._timer = QTimer(self, interval=16, timeout=self.update)
        self._timer.start()

    def sizeHint(self) -> QSize:
        return QSize(480, 150)

    def add(self, lane: str, value: int) -> None:
        self._ticks[lane].append(time.perf_counter())
        self._values[lane] = str(value)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        palette = self.palette()
        painter.fillRect(self.rect(), palette.base())
        now, height = time.perf_counter(), self.height() / len(self._ticks)
        for i, (lane, ticks) in enumerate(self._ticks.items()):
            top = i * height
            # the lane's name, and the last value it received
            painter.setPen(palette.text().color())
            label = QRectF(10, top, LABEL_WIDTH - 20, height)
            align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            painter.drawText(label, align, f"{lane}\n{self._values[lane]}")
            # a tick for each call
            painter.setPen(QPen(QColor(self._colors[lane]), 2))
            for t in ticks:
                x = self.width() - (now - t) * SPEED
                painter.drawLine(QPointF(x, top + 8), QPointF(x, top + height - 8))
            while ticks and self.width() - (now - ticks[0]) * SPEED < LABEL_WIDTH:
                ticks.popleft()


app = QApplication([])

window = QWidget()
slider = QSlider(Qt.Orientation.Horizontal)
slider.setValue(20)
timeline = Timeline(
    {
        "valueChanged": "#8c8c8c",
        "qthrottled (100 ms)": "#3b82f6",
        "qdebounced (300 ms)": "#f59e0b",
    }
)
layout = QVBoxLayout(window)
layout.addWidget(slider)
layout.addWidget(timeline)


@qthrottled(timeout=100)
def throttled(value: int) -> None:
    timeline.add("qthrottled (100 ms)", value)


@qdebounced(timeout=300)
def debounced(value: int) -> None:
    timeline.add("qdebounced (300 ms)", value)


slider.valueChanged.connect(lambda value: timeline.add("valueChanged", value))
slider.valueChanged.connect(throttled)
slider.valueChanged.connect(debounced)

window.show()
app.exec()
