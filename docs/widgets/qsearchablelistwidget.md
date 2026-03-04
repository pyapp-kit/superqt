# QSearchableListWidget

`QSearchableListWidget` is a variant of
[`QListWidget`](https://doc.qt.io/qt-6/qlistwidget.html) that add text entry
above list widget that allow to filter list of available options.

Due to implementation details, this widget it does not inherit directly from
[`QListWidget`](https://doc.qt.io/qt-6/qlistwidget.html) but it does fully
satisfy its api. The only limitation is that it cannot be used as argument of
[`QListWidgetItem`](https://doc.qt.io/qt-6/qlistwidgetitem.html) constructor.

```python
from qtpy.QtWidgets import QApplication

from superqt import QSearchableListWidget

app = QApplication([])

slider = QSearchableListWidget()
slider.addItems(["foo", "bar", "baz", "foobar", "foobaz", "barbaz"])
slider.show()

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.QSearchableListWidget') }}
