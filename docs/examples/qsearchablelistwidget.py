from qtpy.QtWidgets import QApplication

from superqt import QSearchableListWidget

app = QApplication([])

widget = QSearchableListWidget()
widget.addItems(["foo", "bar", "baz", "foobar", "foobaz", "barbaz"])
widget.show()

app.exec()
