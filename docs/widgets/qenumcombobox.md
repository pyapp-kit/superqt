# QEnumComboBox

```python
from enum import Enum

from qtpy.QtWidgets import QApplication
from superqt import QEnumComboBox


class SampleEnum(Enum):
    first = 1
    second = 2
    third = 3

app = QApplication([])

combo = QEnumComboBox()
combo.setEnumClass(SampleEnum)
combo.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QEnumComboBox') }}
