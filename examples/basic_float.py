from qwidgets import QDoubleSlider
from qwidgets.qtcompat.QtCore import Qt
from qwidgets.qtcompat.QtWidgets import QApplication

app = QApplication([])

slider = QDoubleSlider(Qt.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.show()

app.exec_()
