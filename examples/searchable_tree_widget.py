from qtpy.QtWidgets import QApplication

from superqt import QSearchableTreeWidget

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

tree = QSearchableTreeWidget()
tree.setData(data)
tree.show()

app.exec_()
