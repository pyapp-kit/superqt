from qt_extras import QDoubleSlider
from qt_extras.qtcompat.QtCore import Qt
from qt_extras.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QDoubleSlider(Qt.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.show()

app.exec_()
