# QToggleSwitch

A checkable [`QAbstractButton`](https://doc.qt.io/qt-6/qabstractbutton.html)
drawn as a toggle switch, with an optional text label. It's used like a
[`QCheckBox`](https://doc.qt.io/qt-6/qcheckbox.html): `isChecked()`,
`setChecked()`, and the `toggled` signal.

Its colors and size are properties (`onColor`, `offColor`, `handleColor`,
`switchWidth`, `switchHeight`, and `handleSize`), so they can also be set in a
style sheet, as in `QToggleSwitch { qproperty-onColor: red; }`. For other
looks, subclass it and reimplement `drawGroove`, `drawHandle`, or `drawText`,
which are given a `superqt.switch.QStyleOptionToggleSwitch` with the colors and
sizes to use.

{{ show_widget() }}

```python
--8<--
examples/qtoggleswitch.py
--8<--
```

{{ show_members('superqt.QToggleSwitch') }}

::: superqt.switch.QStyleOptionToggleSwitch
    options:
      heading_level: 3
      show_if_no_docstring: true
