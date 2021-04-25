from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QRangeSlider()

slider.setValue((20, 80))
slider.show()

app.exec_()
