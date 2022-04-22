from qtpy.QtWidgets import QApplication

from superqt import QSearchableComboBox

app = QApplication([])

slider = QSearchableComboBox()
slider.addItems(["foo", "bar", "baz", "foobar", "foobaz", "barbaz"])
slider.show()

app.exec_()
