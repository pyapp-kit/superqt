# QRangeSlider

- `QRangeSlider` inherits from [`QSlider`](https://doc.qt.io/qt-5/qslider.html)
  and attempts to match the Qt API as closely as possible
- It uses platform-specific styles (for handle, groove, & ticks) but also supports
  QSS style sheets.
- Supports mouse wheel events
- Supports more than 2 handles (e.g. `slider.setValue([0, 10, 60, 80])`)

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QRangeSlider

app = QApplication([])

slider = QRangeSlider(Qt.Orientation.Horizontal)
slider.setValue((20, 80))
slider.show()

app.exec_()
```

{{ show_widget() }}

As `QRangeSlider` inherits from
[`QtWidgets.QSlider`](https://doc.qt.io/qt-5/qslider.html), you can use all of
the same methods available in the [QSlider
API](https://doc.qt.io/qt-5/qslider.html). The major difference is that `value()`
and `sliderPosition()` are reimplemented as `tuples` of `int` (where the length of
the tuple is equal to the number of handles in the slider.)

{{ show_members('superqt.QRangeSlider') }}
