# QCollapsible

A [`QFrame`](https://doc.qt.io/qt-6/qframe.html) with a header button that
hides or shows its contents, with an animation. Add contents with `addWidget`.

- `expand()` and `collapse()` open and close it from code (pass
  `animate=False` to skip the animation), and `toggled` emits `True` or
  `False` when it opens or closes.
- `setExpandedIcon` and `setCollapsedIcon` change the header's icons (a
  `QIcon`, or a string such as `"▼"`), and `setDuration` and
  `setEasingCurve` change the animation.
- `setLocked(True)` keeps it from opening or closing, until it's unlocked.

{{ show_widget() }}

```python
--8<--
examples/qcollapsible.py
--8<--
```

{{ show_members('superqt.QCollapsible') }}
