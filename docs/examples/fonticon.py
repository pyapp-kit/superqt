from fonticon_fa5 import FA5S
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt.fonticon import icon

app = QApplication([])

button = QPushButton()
button.setIcon(icon(FA5S.smile, color="royalblue"))
button.setIconSize(QSize(96, 96))
button.show()

app.exec()
