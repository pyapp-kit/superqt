from qtpy.QtWidgets import QApplication

from superqt import QRangeSlider

app = QApplication([])

slider = QRangeSlider()
slider.setMinimum(0)
slider.setMaximum(200)
slider.setValue((0, 40, 80, 160))
slider.show()

app.exec_()
