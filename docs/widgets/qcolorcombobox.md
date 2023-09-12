# QColorComboBox

`QComboBox` designed to select from a specific set of colors.

```python
from qtpy.QtWidgets import QApplication

from superqt import QColorComboBox

app = QApplication([])

colors = QColorComboBox()
colors.addColors(['red', 'green', 'blue'])

# show an "Add Color" item that opens a QColorDialog when clicked
colors.setUserColorsAllowed(True)

# emits a QColor when changed
colors.currentColorChanged.connect(print)
colors.show()

app.exec_()
```

{{ show_widget(100) }}

{{ show_members('superqt.QColorComboBox') }}
