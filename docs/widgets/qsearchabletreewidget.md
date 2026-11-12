# QSearchableTreeWidget

A [`QTreeWidget`](https://doc.qt.io/qt-6/qtreewidget.html) that shows a mapping
(such as a `dict`), with a `QLineEdit` above it to filter it. Nested mappings and
sequences become branches of the tree, with keys (or indices) in the first
column and values in the second.

The filter is a [regular expression](https://doc.qt.io/qt-6/qregularexpression.html#details):
an item is shown if its key or value matches it, or if one of its ancestors' or
descendants' does.

Create it with `QSearchableTreeWidget.fromData(data)`. It doesn't watch the
mapping for changes: call `setData` to show new data.

{{ show_widget() }}

```python
--8<--
examples/qsearchabletreewidget.py
--8<--
```

{{ show_members('superqt.QSearchableTreeWidget') }}
