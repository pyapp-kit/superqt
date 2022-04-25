# ListWidget

## QSearchableListWidget

`QSearchableListWidget` is a variant of [`QListWidget`](https://doc.qt.io/qt-5/qlistwidget.html) that add text entry above list widget that allow to filter list
of available options.

Because of implementation it does not inherit directly from `QListWidget` but satisfy it all api. The only limitation is that it cannot be used as argument of `QListWidgetItem` constructor.
