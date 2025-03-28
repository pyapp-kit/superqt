# QEnumComboBox

`QEnumComboBox` is a variant of
[`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) that populates the items in
the combobox based on a python `Enum` class.  In addition to all the methods
provided by `QComboBox`, this subclass adds the methods
`enumClass`/`setEnumClass` to get/set the current `Enum` class represented by
the combobox, and `currentEnum`/`setCurrentEnum` to get/set the current `Enum`
member in the combobox. There is also a new signal `currentEnumChanged(enum)`
analogous to `currentIndexChanged` and `currentTextChanged`.

Method like `insertItem` and `addItem` are blocked and try of its usage will end
with `RuntimeError`

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

Another option is to use optional `enum_class` argument of constructor and change

```python
# option A:
combo = QEnumComboBox()
combo.setEnumClass(SampleEnum)
# option B:
combo = QEnumComboBox(enum_class=SampleEnum)
```

## Allow `None`

`QEnumComboBox` also allows using `Optional` type annotation:

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
combo.setEnumClass(SampleEnum, allow_none=True)
```

In this case there is added option `----` and the `currentEnum()` method will
return `None` when it is selected.

{{ show_members('superqt.QEnumComboBox') }}
