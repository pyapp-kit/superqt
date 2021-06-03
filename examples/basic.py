from qwidgets import QRangeSlider
from qwidgets.qtcompat.QtCore import Qt
from qwidgets.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QRangeSlider(Qt.Horizontal)
slider = QRangeSlider(Qt.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()
