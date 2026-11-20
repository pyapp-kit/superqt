# Blocking signals

`signals_blocked` blocks the signals of one or more `QObject`s while its block
runs, and restores each object's previous state afterwards (like
[`QSignalBlocker`](https://doc.qt.io/qt-6/qsignalblocker.html), as a context
manager):

```python
from superqt.utils import signals_blocked

with signals_blocked(slider):
    slider.setValue(10)  # doesn't emit valueChanged
```

::: superqt.utils.signals_blocked
