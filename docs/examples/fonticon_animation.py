from fonticon_fa5 import FA5S
from qtpy.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget

from superqt.fonticon import icon, pulse, spin

app = QApplication([])

window = QWidget()
layout = QHBoxLayout(window)

spinning = QPushButton("spin")
spinning.setIcon(icon(FA5S.sync, animation=spin(spinning)))
layout.addWidget(spinning)

pulsing = QPushButton("pulse")
pulsing.setIcon(icon(FA5S.spinner, animation=pulse(pulsing)))
layout.addWidget(pulsing)

window.show()
app.exec()
