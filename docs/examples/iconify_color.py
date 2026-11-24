from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

button = QPushButton()
# --8<-- [start:icon]
button.setIcon(QIconifyIcon("bi:bell-fill", color="red", rotate=90))
# --8<-- [end:icon]
button.setIconSize(QSize(48, 48))
button.show()

app.exec()
