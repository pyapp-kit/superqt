from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLabeledRangeSlider

app = QApplication([])

slider = QLabeledRangeSlider(Qt.Orientation.Horizontal)
slider.setValue((20, 80))
slider.show()

app.exec()
