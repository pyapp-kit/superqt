from qtpy.QtGui import QPalette
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

button = QPushButton("Notifications")
# --8<-- [start:icon]
color = button.palette().color(QPalette.ColorRole.ButtonText).name()
button.setIcon(QIconifyIcon("bi:bell", color=color))
# --8<-- [end:icon]
button.show()

app.exec()
