from qt_extras import QDoubleSlider
from qt_extras.qtcompat.QtCore import Qt
from qt_extras.qtcompat.QtWidgets import QApplication

app = QApplication([])

sld = QDoubleSlider(Qt.Horizontal)
sld.setRange(0, 1)
sld.setValue(0.5)
sld.show()

app.exec_()
