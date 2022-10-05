from qtpy.QtWidgets import QApplication

from superqt import QQuantity

app = QApplication([])
w = QQuantity("1m")
w.show()

app.exec()
