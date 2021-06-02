from qtrangeslider import QDoubleSlider
from qtrangeslider.qtcompat.QtCore import Qt
from qtrangeslider.qtcompat.QtWidgets import QApplication

app = QApplication([])

sld = QDoubleSlider(Qt.Horizontal)
sld.setRange(0, 1)
sld.setValue(0.5)
sld.show()

app.exec_()
