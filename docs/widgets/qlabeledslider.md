# QLabeledSlider

A slider with a label next to it that shows the slider's value. The value can
be typed into the label.

`QLabeledSlider` is a [`QAbstractSlider`](https://doc.qt.io/qt-6/qabstractslider.html)
that wraps a `QSlider` and a label; slider methods such as `setRange` and
`setValue` work as they do on a `QSlider`. To move the label to the other side,
or hide it, use `setEdgeLabelPosition` (with `LabelPosition.LabelsLeft` or
`LabelPosition.NoLabel`).

{{ show_widget() }}

```python
--8<--
examples/qlabeledslider.py
--8<--
```

{{ show_members('superqt.QLabeledSlider') }}
