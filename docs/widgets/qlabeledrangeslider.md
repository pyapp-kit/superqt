# QLabeledRangeSlider

Labeled variant of [`QRangeSlider`](qrangeslider.md). (see that page for more details).

```python
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication

from superqt import QLabeledRangeSlider

app = QApplication([])

slider = QLabeledRangeSlider(Qt.Orientation.Horizontal)
slider.setValue((20, 80))
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QLabeledRangeSlider') }}

----

If you find that you need to fine tune the position of the handle labels:

- `QLabeledRangeSlider.label_shift_x`: adjust horizontal label position
- `QLabeledRangeSlider.label_shift_y`: adjust vertical label position
