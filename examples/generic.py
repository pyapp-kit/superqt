from superqt import QDoubleSlider
from superqt.qtcompat.QtCore import Qt
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])

sld = QDoubleSlider(Qt.Orientation.Horizontal)
sld.setRange(0, 1)
sld.setValue(0.5)
sld.show()

app.exec_()
