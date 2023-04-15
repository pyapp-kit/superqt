import logging
from qtpy.QtWidgets import QApplication

from superqt import QSearchableTreeWidget

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s : %(levelname)s : %(filename)s : %(message)s"
)

data = {
    'kermit': 'favorite child',
    'momo': ['loves', 'to', 'eat'],
    'requests': {
        'belly': 'rubs',
        'treats': 'please',
        'bowl': ['full', 'of', 'food'],
    },
    'cuteness': 10,
    'sleep': None,
}

app = QApplication([])

tree = QSearchableTreeWidget.fromData(data)
tree.show()

app.exec_()
