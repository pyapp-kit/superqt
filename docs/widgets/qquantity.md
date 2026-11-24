# QQuantity

A widget for editing a quantity: a magnitude, in a spin box, and a unit, in a
combo box with the units of the same dimension (for meters: millimeters,
kilometers, and so on). The value is a
[`pint.Quantity`](https://pint.readthedocs.io/).

!!! note "Requires pint"

    Install [pint](https://pint.readthedocs.io) with the `quantity` extra:

    ```bash
    pip install "superqt[quantity]"
    ```

{{ show_widget() }}

```python
--8<--
examples/qquantity.py
--8<--
```

!!! warning "Only one dimension"

    `QQuantity` supports units of a single dimension, with an exponent, such as
    `meter ** 2` or `1 / second`. Units that combine dimensions, such as
    `meter / second` or `newton`, raise a `NotImplementedError`.

{{ show_members('superqt.QQuantity') }}
