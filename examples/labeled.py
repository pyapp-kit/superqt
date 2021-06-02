from qtrangeslider._labeled import (
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
)
from qtrangeslider.qtcompat.QtCore import Qt
from qtrangeslider.qtcompat.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

app = QApplication([])

ORIENTATION = Qt.Horizontal

w = QWidget()
qls = QLabeledSlider(ORIENTATION)
qls.valueChanged.connect(lambda e: print("qls valueChanged", e))
qls.setRange(0, 500)
qls.setValue(300)


qlds = QLabeledDoubleSlider(ORIENTATION)
qlds.valueChanged.connect(lambda e: print("qlds valueChanged", e))
qlds.setRange(0, 1)
qlds.setValue(0.5)
qlds.setSingleStep(0.1)

qlrs = QLabeledRangeSlider(ORIENTATION)
qlrs.valueChanged.connect(lambda e: print("QLabeledRangeSlider valueChanged", e))
qlrs.setValue((20, 60))

qldrs = QLabeledDoubleRangeSlider(ORIENTATION)
qldrs.valueChanged.connect(lambda e: print("qlrs valueChanged", e))
qldrs.setRange(0, 1)
qldrs.setSingleStep(0.01)
qldrs.setValue((0.2, 0.7))


w.setLayout(QVBoxLayout() if ORIENTATION == Qt.Horizontal else QHBoxLayout())
w.layout().addWidget(qls)
w.layout().addWidget(qlds)
w.layout().addWidget(qlrs)
w.layout().addWidget(qldrs)
w.show()
w.resize(500, 150)
app.exec_()
