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

{{ show_widget() }}

```python
--8<--
examples/qquantity.py
--8<--
```

!!! note

    `QQuantity` currently supports simple units with exponents, e.g., `meters^2` or
    `1/second`. However, compound units, e.g. `meter/second`, `Newton`, etc.,
    are not currently supported.

{{ show_members('superqt.QQuantity') }}
