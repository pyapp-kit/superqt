from superqt import QRangeSlider
from superqt.qtcompat.QtCore import Qt
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QRangeSlider(Qt.Horizontal)
slider = QRangeSlider(Qt.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()
