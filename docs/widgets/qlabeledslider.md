# QLabeledSlider

{{ insert_example('

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

') }}

{{ show_members('superqt.QLabeledSlider') }}
