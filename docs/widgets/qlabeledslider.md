# QLabeledSlider

`QSlider` variant that shows an editable (SpinBox) label next to the slider.

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLabeledSlider

app = QApplication([])

slider = QLabeledSlider(Qt.Orientation.Horizontal)
slider.setValue(42)
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QLabeledSlider') }}
