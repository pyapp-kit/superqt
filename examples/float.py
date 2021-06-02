from qtrangeslider import QDoubleRangeSlider, QDoubleSlider, QRangeSlider
from qtrangeslider.qtcompat.QtCore import Qt
from qtrangeslider.qtcompat.QtWidgets import QApplication, QVBoxLayout, QWidget

app = QApplication([])

w = QWidget()

sld1 = QDoubleSlider(Qt.Horizontal)
sld2 = QDoubleRangeSlider(Qt.Horizontal)
rs = QRangeSlider(Qt.Horizontal)

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
