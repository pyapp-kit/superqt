from qtpy.QtWidgets import QApplication

from superqt import QToggleSwitch

app = QApplication([])

switch = QToggleSwitch()
switch.show()

app.exec()
