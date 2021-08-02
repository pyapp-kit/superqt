# ComboBox


## Enum Combo Box

`QEnumComboBox` is a variant of [`QComboBox`](https://doc.qt.io/qt-5/qcombobox.html) 
that populates the items in the combobox based on a python `Enum` class.  In addition to all 
of the methods provided by `QComboBox`, this subclass adds the methods 
`enumClass`/`setEnumClass` to get/set the current `Enum` class represented by the combobox, 
and `currentEnum`/`setCurrentEnum` to get/set the current `Enum` member in the combobox

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
