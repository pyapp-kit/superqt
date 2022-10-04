# Widgets

The following are QWidget subclasses:

## Sliders and Numerical Inputs

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QDoubleSlider`](./qdoubleslider.md)             | Slider for float values |
| [`QLabeledSlider`](./qlabeledslider.md)            | `QSlider` with editable `QSpinBox` that shows the current value |
| [`QLabeledDoubleSlider`](./qlabeleddoubleslider.md)      | `QSlider` for float values with editable `QSpinBox` with the current value |
| [`QRangeSlider`](./qrangeslider.md)              | Multi-handle slider   |
| [`QDoubleRangeSlider`](./qdoublerangeslider.md)        | Multi-handle slider for float values   |
| [`QLabeledRangeSlider`](./qlabeledrangeslider.md)       | `QRangeSlider` variant, with editable labels for each handle |
| [`QLabeledDoubleRangeSlider`](./qlabeleddoublerangeslider.md) | `QDoubleRangeSlider` variant with editable labels for each handle |
| [`QLargeIntSpinBox`](./qlargeintspinbox.md)          | `QSpinbox` that accepts arbitrarily large integers |

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
