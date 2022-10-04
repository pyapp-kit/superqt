# QSearchableComboBox

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
