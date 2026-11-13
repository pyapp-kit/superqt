from qtpy.QtWidgets import QApplication

from superqt.cmap import QColormapLineEdit

app = QApplication([])

line_edit = QColormapLineEdit()
line_edit.setText("viridis")
line_edit.show()

app.exec()
