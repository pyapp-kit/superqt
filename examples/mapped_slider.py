from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QFormLayout, QWidget

from superqt import QLabeledDoubleSlider, QLabeledMappedSlider

app = QApplication([])

linear = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
linear.setRange(0, 0.5)
linear.setDecimals(3)
linear.valueChanged.connect(lambda v: print("linear", v))

log = QLabeledMappedSlider(Qt.Orientation.Horizontal, mapping="log")
log.setRange(0.001, 1)
log.setDecimals(4)
log.valueChanged.connect(lambda v: print("log", v))

power = QLabeledMappedSlider(Qt.Orientation.Horizontal, mapping="power", exponent=3)
power.setRange(0, 0.5)
power.setDecimals(4)
power.valueChanged.connect(lambda v: print("power", v))

w = QWidget()
layout = QFormLayout(w)
layout.addRow("linear (0 to 0.5)", linear)
layout.addRow("log (0.001 to 1)", log)
layout.addRow("power 3 (0 to 0.5)", power)
w.resize(500, 120)
w.show()

app.exec()
