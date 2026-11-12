# QSearchableTreeWidget

`QSearchableTreeWidget` combines a
[`QTreeWidget`](https://doc.qt.io/qt-6/qtreewidget.html) and a `QLineEdit` for showing a mapping that can be searched by key.

This is intended to be used with a read-only mapping and be conveniently created
using `QSearchableTreeWidget.fromData(data)`. If the mapping changes, the
easiest way to update this is by calling `setData`.

{{ show_widget() }}

```python
--8<--
examples/qsearchabletreewidget.py
--8<--
```

{{ show_members('superqt.QSearchableTreeWidget') }}
