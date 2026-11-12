# QSearchableListWidget

`QSearchableListWidget` is a variant of
[`QListWidget`](https://doc.qt.io/qt-6/qlistwidget.html) that add text entry
above list widget that allow to filter list of available options.

Due to implementation details, this widget it does not inherit directly from
[`QListWidget`](https://doc.qt.io/qt-6/qlistwidget.html) but it does fully
satisfy its api. The only limitation is that it cannot be used as argument of
[`QListWidgetItem`](https://doc.qt.io/qt-6/qlistwidgetitem.html) constructor.

{{ show_widget() }}

```python
--8<--
examples/qsearchablelistwidget.py
--8<--
```

{{ show_members('superqt.QSearchableListWidget') }}
