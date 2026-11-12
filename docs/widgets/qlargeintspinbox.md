# QLargeIntSpinBox

A spin box for integers of any size. `QSpinBox` stores its value in a 32-bit
integer, so it can't go beyond ±2,147,483,647; `QLargeIntSpinBox` stores a
Python `int`, and its default maximum is `2**64 - 1`.

It doesn't support the prefix, suffix, or special value text of `QSpinBox`.
Its `valueChanged` signal emits an `object` (a Python `int`), because a Qt
`int` couldn't carry large values.

{{ show_widget() }}

```python
--8<--
examples/qlargeintspinbox.py
--8<--
```

{{ show_members('superqt.QLargeIntSpinBox') }}
