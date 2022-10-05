from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QDoubleSlider

app = QApplication([])

slider = QDoubleSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.resize(500, 50)
slider.show()

app.exec_()
