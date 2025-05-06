# QSearchableComboBox

`QSearchableComboBox` is a variant of
[`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) that allow to filter list
of options by enter part of text. It could be drop in replacement for
`QComboBox`.


```python
from qtpy.QtWidgets import QApplication

from superqt import QSearchableComboBox

app = QApplication([])

combo = QSearchableComboBox()
combo.addItems(["foo", "bar", "baz", "foobar", "foobaz", "barbaz"])
combo.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QSearchableComboBox') }}
