from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

button = QPushButton("Notifications")
# --8<-- [start:icon]
icon = QIconifyIcon("bi:bell", color="gray")
icon.addKey("bi:bell-fill", color="orange", state=QIcon.State.On)
button.setCheckable(True)
button.setIcon(icon)
# --8<-- [end:icon]
button.show()

app.exec()
