---
hide:
  - toc
---

# Widgets

Most of these widgets subclass the Qt widget they're most similar to, and follow
Qt's API conventions (`camelCase` names, `value()`/`setValue()` pairs, and
signals named like `valueChanged`), so they can be used wherever that widget
is. Each page lists the Qt class and what superqt adds to it.

## Sliders

<div class="sq-gallery" markdown>
{{ card("qrangeslider.md", "QRangeSlider", "A slider with two or more handles, to select a range.") }}
{{ card("qdoubleslider.md", "QDoubleSlider", "A slider for floats.") }}
{{ card("qdoublerangeslider.md", "QDoubleRangeSlider", "A range slider for floats.") }}
{{ card("qlabeledslider.md", "QLabeledSlider", "A slider with an editable label for its value.") }}
{{ card("qlabeleddoubleslider.md", "QLabeledDoubleSlider", "A slider for floats, with an editable label for its value.") }}
{{ card("qlabeledrangeslider.md", "QLabeledRangeSlider", "A range slider with editable labels for its handles and range.") }}
{{ card("qlabeleddoublerangeslider.md", "QLabeledDoubleRangeSlider", "A range slider for floats, with editable labels.") }}
</div>

## Numeric inputs

<div class="sq-gallery" markdown>
{{ card("qlargeintspinbox.md", "QLargeIntSpinBox", "A spin box for integers of any size.") }}
{{ card("qquantity.md", "QQuantity", "A magnitude and a unit, backed by pint.") }}
</div>

## Combo boxes

<div class="sq-gallery" markdown>
{{ card("qenumcombobox.md", "QEnumComboBox", "A combo box with the members of an `Enum`.") }}
{{ card("qsearchablecombobox.md", "QSearchableComboBox", "A combo box that filters its items as you type.") }}
{{ card("qcolorcombobox.md", "QColorComboBox", "A combo box for choosing a color.") }}
{{ card("qcolormap.md", "QColormapComboBox", "A combo box for choosing a colormap.") }}
{{ card("colormap_catalog.md", "CmapCatalogComboBox", "A searchable combo box with every colormap in the cmap catalog.") }}
</div>

## Lists and trees

<div class="sq-gallery" markdown>
{{ card("qsearchablelistwidget.md", "QSearchableListWidget", "A list with a text field that filters its items.") }}
{{ card("qsearchabletreewidget.md", "QSearchableTreeWidget", "A tree view of a mapping, filtered by a regular expression.") }}
</div>

## Text and buttons

<div class="sq-gallery" markdown>
{{ card("qelidinglabel.md", "QElidingLabel", "A label that shortens its text with an ellipsis to fit.") }}
{{ card("qelidinglineedit.md", "QElidingLineEdit", "A line edit that shortens its text with an ellipsis while it isn't being edited.") }}
{{ card("qcolormaplineedit.md", "QColormapLineEdit", "A line edit that shows the colormap that its text names.") }}
{{ card("qtoggleswitch.md", "QToggleSwitch", "A checkable button drawn as a toggle switch.") }}
</div>

## Containers and layouts

<div class="sq-gallery" markdown>
{{ card("qcollapsible.md", "QCollapsible", "A frame that hides or shows its contents when its header is clicked.") }}
{{ card("qflowlayout.md", "QFlowLayout", "A layout that wraps its items onto new rows to fit the width.") }}
</div>
