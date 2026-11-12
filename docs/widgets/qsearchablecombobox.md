# QSearchableComboBox

A [`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) that you can type into:
it shows a list of the items that contain the typed text (ignoring case), to
choose from. Items are added as in a `QComboBox`, and typed text that doesn't
match an item isn't added to it.

{{ show_widget() }}

```python
--8<--
examples/qsearchablecombobox.py
--8<--
```

{{ show_members('superqt.QSearchableComboBox') }}
