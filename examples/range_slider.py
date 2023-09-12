from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QRangeSlider

app = QApplication([])

slider = QRangeSlider(Qt.Orientation.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()
