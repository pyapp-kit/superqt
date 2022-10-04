# QDoubleRangeSlider

Float variant of [`QRangeSlider`](qrangeslider.md). (see that page for more details).

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QDoubleRangeSlider

app = QApplication([])

slider = QDoubleRangeSlider(Qt.Orientation.Horizontal)
slider.setRange(0, 1)
slider.setValue((0.2, 0.8))
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QDoubleRangeSlider') }}
