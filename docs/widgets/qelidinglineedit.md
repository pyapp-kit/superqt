# QElidingLineEdit

A [`QLineEdit`](https://doc.qt.io/qt-6/qlineedit.html) that elides its text while
it isn't being edited: when the text is too long to fit, its end is replaced with
an ellipsis ("…"). When the line edit has focus, it shows the full text, for
editing. `text()` always returns the full text.

As with [`QElidingLabel`](qelidinglabel.md), `setElideMode` sets which part of the
text is elided.

{{ show_widget() }}

```python
--8<--
examples/qelidinglineedit.py
--8<--
```

{{ show_members('superqt.QElidingLineEdit') }}
