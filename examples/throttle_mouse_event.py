from qtpy.QtCore import Signal
from qtpy.QtWidgets import QApplication, QWidget

from superqt.utils import qthrottled


class Demo(QWidget):
    positionChanged = Signal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setMouseTracking(True)
        self.positionChanged.connect(self._show_location)

    @qthrottled(timeout=400)  # call this no more than once every 400ms
    def _show_location(self, x, y):
        print("Throttled event at", x, y)

    def mouseMoveEvent(self, event):
        print("real move event at", event.x(), event.y())
        self.positionChanged.emit(event.x(), event.y())


if __name__ == "__main__":
    app = QApplication([])
    w = Demo()
    w.resize(600, 600)
    w.show()
    app.exec_()
