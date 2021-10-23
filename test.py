import os

from PySide2 import QtCore, QtGui, QtWidgets


class RotateMe(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pixmap = QtGui.QPixmap()
        self._animation = QtCore.QVariantAnimation(
            self,
            startValue=0.0,
            endValue=360.0,
            duration=1000,
            valueChanged=self.on_valueChanged,
        )

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.setPixmap(self._pixmap)

    def start_animation(self):
        if self._animation.state() != QtCore.QAbstractAnimation.Running:
            self._animation.start()

    @QtCore.pyqtSlot(QtCore.QVariant)
    def on_valueChanged(self, value):
        t = QtGui.QTransform()
        t.rotate(value)
        self.setPixmap(self._pixmap.transformed(t))


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = RotateMe(alignment=QtCore.Qt.AlignCenter)
        img_path = os.path.join("path/to/image", "image.svg")
        label.set_pixmap(QtGui.QPixmap(img_path))
        button = QtWidgets.QPushButton("Rotate")

        button.clicked.connect(label.start_animation)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(label)
        lay.addWidget(button)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
