# Widgets

The following are QWidget subclasses:

## Sliders and Numerical Inputs

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QDoubleSlider`]()             | Slider for float values |
| [`QLabeledSlider`]()            | `QSlider` with editable `QSpinBox` that shows the current value |
| [`QLabeledDoubleSlider`]()      | `QSlider` for float values with editable `QSpinBox` with the current value |
| [`QRangeSlider`]()              | Multi-handle slider   |
| [`QDoubleRangeSlider`]()        | Multi-handle slider for float values   |
| [`QLabeledRangeSlider`]()       | `QRangeSlider` variant, with editable labels for each handle |
| [`QLabeledDoubleRangeSlider`]() | `QDoubleRangeSlider` variant with editable labels for each handle |
| [`QLargeIntSpinBox`]()          | `QSpinbox` that accepts arbitrarily large integers |

## Labels and categorical inputs

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QSearchableListWidget`]()     | `QListWidget` variant with search field that filters available options |
| [`QEnumComboBox`]()             | `QComboBox` that populates the combobox from a python `Enum` |
| [`QSearchableComboBox`]()       | `QComboBox` variant that filters available options based on text input |
| [`QElidingLabel`]()             | A `QLabel` variant that will elide text (add `…`) to fit width. |

## Frames and containers

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QCollapsible`](./qcollapsible.md)              | A collapsible widget to hide and unhide child widgets. |
