# QColorComboBox

A [`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) for choosing a color
from a list. Colors can be given as anything that `QColor` accepts (names,
hex strings, `QColor`s, and so on); `currentColor()` returns a `QColor`, and
`currentColorChanged` emits one.

- With `setUserColorsAllowed(True)` (or `allow_user_colors=True`), an
  "Add Color..." item at the end of the list opens a `QColorDialog`, and adds
  the chosen color.
- `setInvalidColorPolicy` sets what happens when an invalid color is added:
  it's ignored (`InvalidColorPolicy.Ignore`, the default), or it causes a
  warning (`Warn`) or an exception (`Raise`).

{{ show_widget() }}

```python
--8<--
examples/qcolorcombobox.py
--8<--
```

{{ show_members('superqt.QColorComboBox') }}
