import logging

from qtpy.QtWidgets import QApplication

from superqt import QSearchableTreeWidget

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s : %(levelname)s : %(filename)s : %(message)s",
)

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

app = QApplication([])

tree = QSearchableTreeWidget.fromData(data)
tree.show()

app.exec_()
