# QElidingLabel

A [`QLabel`](https://doc.qt.io/qt-6/qlabel.html) that elides its text: when the
text is too long to fit, its end is replaced with an ellipsis ("…"). `text()`
still returns the full text.

- `setElideMode` sets which part of the text is elided (the end, by default;
  or the start or the middle), with a `Qt.TextElideMode`.
- With `setWordWrap(True)`, the text wraps onto as many lines as fit, and only
  the last line is elided.

For a line edit that does the same, see [`QElidingLineEdit`](qelidinglineedit.md).

{{ show_widget() }}

```python
--8<--
examples/qelidinglabel.py
--8<--
```

{{ show_members('superqt.QElidingLabel') }}
