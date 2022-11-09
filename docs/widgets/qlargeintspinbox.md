# QLargeIntSpinBox

`QSpinBox` variant that allows to enter large integers, without overflow.

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLargeIntSpinBox

app = QApplication([])

slider = QLargeIntSpinBox()
slider.setRange(0, 4.53e8)
slider.setValue(4.53e8)
slider.show()

app.exec_()
```

{{ show_widget(150) }}

{{ show_members('superqt.QLargeIntSpinBox') }}
