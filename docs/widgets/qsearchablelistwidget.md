# QSearchableListWidget

A [`QListWidget`](https://doc.qt.io/qt-6/qlistwidget.html) with a text field
above it. Typing in the field hides the items that don't contain the text
(ignoring case).

`QSearchableListWidget` is a `QWidget` that contains a `QListWidget`
(`list_widget`) and a `QLineEdit` (`filter_widget`), and forwards the methods of
`QListWidget` to the list, so it can be used like one. The difference is that it
isn't a `QListWidget`: it can't be passed as the parent of a `QListWidgetItem`
(use `list_widget` instead), and `isinstance` checks for `QListWidget` fail.

{{ show_widget() }}

```python
--8<--
examples/qsearchablelistwidget.py
--8<--
```

{{ show_members('superqt.QSearchableListWidget') }}
