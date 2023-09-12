# QSearchableTreeWidget

`QSearchableTreeWidget` combines a
[`QTreeWidget`](https://doc.qt.io/qt-6/qtreewidget.html) and a `QLineEdit` for showing a mapping that can be searched by key.

This is intended to be used with a read-only mapping and be conveniently created
using `QSearchableTreeWidget.fromData(data)`. If the mapping changes, the
easiest way to update this is by calling `setData`.


```python
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
tree.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QSearchableTreeWidget') }}
