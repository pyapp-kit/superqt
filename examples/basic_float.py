from qtrangeslider import QDoubleSlider
from qtrangeslider.qtcompat.QtCore import Qt
from qtrangeslider.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QDoubleSlider(Qt.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.show()

app.exec_()
