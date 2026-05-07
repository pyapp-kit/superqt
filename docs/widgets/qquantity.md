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

!!! note

    `QQuantity` currently supports simple units with exponents, e.g., `meters^2` or
    `1/second`. However, compound units, e.g. `meter/second`, `Newton`, etc.,
    are not currently supported.

{{ show_widget(150) }}

{{ show_members('superqt.QQuantity') }}
