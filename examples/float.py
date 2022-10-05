from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

from superqt import QDoubleRangeSlider, QDoubleSlider, QRangeSlider

app = QApplication([])

w = QWidget()

sld1 = QDoubleSlider(Qt.Orientation.Horizontal)
sld2 = QDoubleRangeSlider(Qt.Orientation.Horizontal)
rs = QRangeSlider(Qt.Orientation.Horizontal)

sld1.valueChanged.connect(lambda e: print("doubslider valuechanged", e))

sld2.setMaximum(1)
sld2.setValue((0.2, 0.8))
sld2.valueChanged.connect(lambda e: print("valueChanged", e))
sld2.sliderMoved.connect(lambda e: print("sliderMoved", e))
sld2.rangeChanged.connect(lambda e, f: print("rangeChanged", (e, f)))

w.setLayout(QVBoxLayout())
w.layout().addWidget(sld1)
w.layout().addWidget(sld2)
w.layout().addWidget(rs)
w.show()
w.resize(500, 150)
app.exec_()
