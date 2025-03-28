# QToggleSwitch

`QToggleSwitch` is a
[`QAbstractButton`](https://doc.qt.io/qt-6/qabstractbutton.html) subclass
that represents a boolean value as a toggle switch. The API is similar to
[`QCheckBox`](https://doc.qt.io/qt-6/qcheckbox.html) but with a different
visual representation.

```python
from qtpy.QtWidgets import QApplication

from superqt import QToggleSwitch

app = QApplication([])

switch = QToggleSwitch()
switch.show()

app.exec_()
```

{{ show_widget(80) }}

{{ show_members('superqt.QToggleSwitch') }}
