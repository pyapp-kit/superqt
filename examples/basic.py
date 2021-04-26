from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat.QtCore import Qt
from qtrangeslider.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QRangeSlider(Qt.Horizontal)

slider.setValue((20, 80))
slider.show()

app.exec_()
