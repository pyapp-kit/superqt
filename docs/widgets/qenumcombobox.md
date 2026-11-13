# QEnumComboBox

A [`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) with the members of a
Python `Enum` as its items. In addition to the `QComboBox` API, it has:

- `enumClass()` and `setEnumClass()`, to get and set the `Enum`;
- `currentEnum()` and `setCurrentEnum()`, to get and set the current member;
- a `currentEnumChanged` signal, which emits the new member.

Items are shown as `str(member)` if the `Enum` defines `__str__`, and otherwise
as the member's name, with underscores replaced by spaces. The items can only
come from the `Enum`: `addItem`, `addItems`, `insertItem`, and `insertItems`
raise a `RuntimeError`.

{{ show_widget() }}

```python
--8<--
examples/qenumcombobox.py
--8<--
```

The `Enum` can also be passed to the constructor:

```python
# option A:
combo = QEnumComboBox()
combo.setEnumClass(SampleEnum)
# option B:
combo = QEnumComboBox(enum_class=SampleEnum)
```

## Allow `None`

With `allow_none=True`, the combo box has an extra item, `----`, for no
member:

```python
from enum import Enum

from superqt import QEnumComboBox


class SampleEnum(Enum):
    first = 1
    second = 2
    third = 3


# (a QApplication must exist before creating a widget)
combo = QEnumComboBox()
combo.setEnumClass(SampleEnum, allow_none=True)
```

When it's selected, `currentEnum()` returns `None` (and `setCurrentEnum(None)`
selects it).

{{ show_members('superqt.QEnumComboBox') }}
