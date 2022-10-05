from qtpy.QtWidgets import QApplication

from superqt import QSearchableListWidget

app = QApplication([])

slider = QSearchableListWidget()
slider.addItems(["foo", "bar", "baz", "foobar", "foobaz", "barbaz"])
slider.show()

app.exec_()
