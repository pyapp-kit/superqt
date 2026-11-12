from fonticon_fa5 import FA5S
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt.fonticon import icon

app = QApplication([])

btn2 = QPushButton()
btn2.setIcon(icon(FA5S.smile, color="blue"))
btn2.setIconSize(QSize(225, 225))
btn2.show()

app.exec()
