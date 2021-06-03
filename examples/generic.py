from qwidgets import QDoubleSlider
from qwidgets.qtcompat.QtCore import Qt
from qwidgets.qtcompat.QtWidgets import QApplication

app = QApplication([])

sld = QDoubleSlider(Qt.Horizontal)
sld.setRange(0, 1)
sld.setValue(0.5)
sld.show()

app.exec_()
