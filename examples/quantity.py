from superqt import QQuantity
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])
w = QQuantity()
w.setValue("1m")
w.show()

app.exec()
