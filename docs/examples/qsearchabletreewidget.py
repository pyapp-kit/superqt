from qtpy.QtWidgets import QApplication

from superqt import QSearchableTreeWidget

app = QApplication([])

data = {
    "none": None,
    "str": "test",
    "int": 42,
    "list": [2, 3, 5],
    "dict": {
        "float": 0.5,
        "tuple": (22, 99),
        "bool": False,
    },
}
tree = QSearchableTreeWidget.fromData(data)
tree.tree.expandAll()
tree.show()

app.exec()
