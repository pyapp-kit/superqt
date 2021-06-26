from superqt import QDoubleSlider
from superqt.qtcompat.QtCore import Qt
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QDoubleSlider(Qt.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.show()

app.exec_()
