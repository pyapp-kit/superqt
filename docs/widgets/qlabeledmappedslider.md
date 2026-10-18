# QLabeledMappedSlider

[`QLabeledDoubleSlider`](./qlabeleddoubleslider.md) variant where the slider position is mapped to the value using a log or power curve.

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLabeledMappedSlider

app = QApplication([])

slider = QLabeledMappedSlider(Qt.Orientation.Horizontal)
slider.setMapping("log")
slider.setRange(1, 100)
slider.setValue(10)
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QLabeledMappedSlider') }}
