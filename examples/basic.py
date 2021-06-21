from qt_extras import QRangeSlider
from qt_extras.qtcompat.QtCore import Qt
from qt_extras.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QRangeSlider(Qt.Horizontal)
slider = QRangeSlider(Qt.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()
