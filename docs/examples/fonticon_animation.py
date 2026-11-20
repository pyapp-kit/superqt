from fonticon_fa5 import FA5S
from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget

from superqt.fonticon import icon, pulse, spin

app = QApplication([])

window = QWidget()
layout = QHBoxLayout(window)
color = window.palette().color(QPalette.ColorRole.ButtonText).name()  # (dark themes)

spinning = QPushButton("spin")
spinning.setIcon(icon(FA5S.sync, color=color, animation=spin(spinning)))
layout.addWidget(spinning)

pulsing = QPushButton("pulse")
pulsing.setIcon(icon(FA5S.spinner, color=color, animation=pulse(pulsing)))
layout.addWidget(pulsing)

window.show()
app.exec()
