# QFlowLayout

QLayout that rearranges items based on parent width.

```python
from qtpy.QtWidgets import QApplication, QPushButton, QWidget

from superqt import QFlowLayout

app = QApplication([])

wdg = QWidget()

layout = QFlowLayout(wdg)
layout.addWidget(QPushButton("Short"))
layout.addWidget(QPushButton("Longer"))
layout.addWidget(QPushButton("Different text"))
layout.addWidget(QPushButton("More text"))
layout.addWidget(QPushButton("Even longer button text"))

wdg.setWindowTitle("Flow Layout")
wdg.show()

app.exec()
```

{{ show_widget(350) }}

{{ show_members('superqt.QFlowLayout') }}
