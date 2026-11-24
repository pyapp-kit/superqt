from qtpy.QtWidgets import QApplication

from superqt import QLargeIntSpinBox

app = QApplication([])

spin = QLargeIntSpinBox()
spin.setRange(0, 10**15)
spin.setValue(2**40)  # a QSpinBox can't go above 2**31 - 1
spin.show()

app.exec()
