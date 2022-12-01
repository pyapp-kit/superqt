# QDoubleSlider

`QSlider` variant that accepts floating point values.

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QDoubleSlider

app = QApplication([])

slider = QDoubleSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 1)
slider.setValue(0.5)
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QDoubleSlider') }}
