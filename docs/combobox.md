# ComboBox


## Enum Combo Box

```python
from enum import Enum

from superqt import QEnumComboBox

class SampleEnum(Enum):
    first = 1
    second = 2
    third = 3

# as usual:
# you must create a QApplication before create a widget.

combo = QEnumComboBox()
combo.setEnumClass(SampleEnum)
```

other option is to use optional `enum_class` argument of constructor and change
```python
combo = QEnumComboBox()
combo.setEnumClass(SampleEnum)
```
to
```python
combo = QEnumComboBox(enum_class=SampleEnum)
```
