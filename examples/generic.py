from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QDoubleSlider

app = QApplication([])

sld = QDoubleSlider(Qt.Orientation.Horizontal)
sld.setRange(0, 1)
sld.setValue(0.5)
sld.show()

app.exec_()
