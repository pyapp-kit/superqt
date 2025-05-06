# Widgets

The following are QWidget subclasses:

## Sliders and Numerical Inputs

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QDoubleRangeSlider`](./qdoublerangeslider.md) | Multi-handle slider for float values   |
| [`QDoubleSlider`](./qdoubleslider.md) | Slider for float values |
| [`QLabeledDoubleRangeSlider`](./qlabeleddoublerangeslider.md) | `QDoubleRangeSlider` variant with editable labels for each handle |
| [`QLabeledDoubleSlider`](./qlabeleddoubleslider.md) | `QSlider` for float values with editable `QSpinBox` with the current value |
| [`QLabeledRangeSlider`](./qlabeledrangeslider.md) | `QRangeSlider` variant, with editable labels for each handle |
| [`QLabeledSlider`](./qlabeledslider.md) | `QSlider` with editable `QSpinBox` that shows the current value |
| [`QLargeIntSpinBox`](./qlargeintspinbox.md) | `QSpinbox` that accepts arbitrarily large integers |
| [`QRangeSlider`](./qrangeslider.md) | Multi-handle slider   |
| [`QQuantity`](./qquantity.md) | Pint-backed quantity widget (magnitude combined with unit dropdown)   |

## Labels and categorical inputs

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QElidingLabel`](./qelidinglabel.md)             | A `QLabel` variant that will elide text (add `…`) to fit width. |
| [`QEnumComboBox`](./qenumcombobox.md)             | `QComboBox` that populates the combobox from a python `Enum` |
| [`QSearchableComboBox`](./qsearchablecombobox.md)       | `QComboBox` variant that filters available options based on text input |
| [`QSearchableListWidget`](./qsearchablelistwidget.md)     | `QListWidget` variant with search field that filters available options |
| [`QSearchableTreeWidget`](./qsearchabletreewidget.md)     | `QTreeWidget` variant with search field that filters available options |
| [`QColorComboBox`](./qcolorcombobox.md)            | `QComboBox` to select from a specified set of colors |
| [`QColormapComboBox`](./qcolormap.md)            | `QComboBox` to select from a specified set of colormaps. |
| [`QToggleSwitch`](./qtoggleswitch.md)            | `QAbstractButton` that represents a boolean value with a toggle switch. |

## Frames and containers

| Widget                          | Description           |
| -----------                     | --------------------- |
| [`QCollapsible`](./qcollapsible.md)              | A collapsible widget to hide and unhide child widgets. |
| [`QFlowLayout`](./qflowlayout.md)                | A layout that rearranges items based on parent width. |
