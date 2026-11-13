# QLabeledRangeSlider

A [`QRangeSlider`](qrangeslider.md) with labels: one above each handle, with
its value, and one at each end, with the minimum and maximum. A value typed
into a handle's label moves that handle, and a value typed into an end label
changes the minimum or maximum.

- `setHandleLabelPosition` moves the handle labels: above
  (`LabelPosition.LabelsAbove`, the default), below, on the handles
  (`LabelPosition.LabelsOnHandle`), or nowhere (`LabelPosition.NoLabel`).
- `setEdgeLabelMode` sets what the end labels show: the range
  (`EdgeLabelMode.LabelIsRange`, the default), the values of the first and
  last handles (`EdgeLabelMode.LabelIsValue`; then typing into them moves those
  handles), or nothing (`EdgeLabelMode.NoLabel`).
- With `setExpandRangeOnHandleEdit(True)`, typing a value outside of the range
  into a handle's label expands the range to include it.

{{ show_widget() }}

```python
--8<--
examples/qlabeledrangeslider.py
--8<--
```

!!! tip "Fine-tuning the label positions"

    The `label_shift_x` and `label_shift_y` attributes offset the handle labels
    by that many pixels.

{{ show_members('superqt.QLabeledRangeSlider') }}
