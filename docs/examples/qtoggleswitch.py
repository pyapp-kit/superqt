from qtpy.QtWidgets import QApplication

from superqt import QToggleSwitch

app = QApplication([])

switch = QToggleSwitch("Notifications")
switch.toggled.connect(print)
switch.show()

app.exec()
