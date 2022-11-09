# QElidingLabel

`QLabel` variant that will elide text (i.e. add an ellipsis)
if it is too long to fit in the available space.

```python
from qtpy.QtWidgets import QApplication

from superqt import QElidingLabel

app = QApplication([])

widget = QElidingLabel(
    "a skj skjfskfj sdlf sdfl sdlfk jsdf sdlkf jdsf dslfksdl sdlfk sdf sdl "
    "fjsdlf kjsdlfk laskdfsal as lsdfjdsl kfjdslf asfd dslkjfldskf sdlkfj"
)
widget.setWordWrap(True)
widget.resize(300, 20)
widget.show()

app.exec_()
```

{{ show_widget(300) }}

{{ show_members('superqt.QElidingLabel') }}
