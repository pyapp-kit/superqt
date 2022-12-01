# QQuantity

A widget that allows the user to edit a quantity (a magnitude associated with a unit).

!!! note

    This widget requires [`pint`](https://pint.readthedocs.io):

    ```
    pip install pint
    ```

    or

    ```
    pip install superqt[quantity]
    ```

```python
from qtpy.QtWidgets import QApplication

from superqt import QQuantity

app = QApplication([])
w = QQuantity("1m")
w.show()

app.exec()
```

{{ show_widget(150) }}

{{ show_members('superqt.QQuantity') }}
