from qtpy.QtWidgets import QApplication

from superqt import QLargeIntSpinBox

app = QApplication([])

slider = QLargeIntSpinBox()
slider.setRange(0, 4.53e8)
slider.setValue(4.53e8)
slider.show()

app.exec()
