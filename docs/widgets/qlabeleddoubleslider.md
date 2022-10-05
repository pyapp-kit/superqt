# QLabeledDoubleSlider

[`QDoubleSlider`](./qdoubleslider.md) variant that shows an editable (SpinBox) label next to the slider.


```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLabeledDoubleSlider

app = QApplication([])

slider = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 2.5)
slider.setValue(1.3)
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QLabeledDoubleSlider') }}
