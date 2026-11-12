---
hide:
  - navigation
  - toc
---

<div class="sq-hero" markdown>
<div class="sq-hero__text" markdown>

# superqt

<p class="sq-lead">"Missing" widgets and components for PyQt and PySide.</p>

This repository aims to provide high-quality community-contributed Qt widgets
and components for [PyQt](https://riverbankcomputing.com/software/pyqt/) &
[PySide](https://www.qt.io/qt-for-python) that are not provided in the native
QtWidgets module.

[Widgets](widgets/index.md){ .md-button .md-button--primary }
[Utilities](utilities/index.md){ .md-button }

</div>

{{ show_widget("showcase") }}

</div>

## Installation

=== "pip"

    ```bash
    pip install superqt
    ```

=== "uv"

    ```bash
    uv add superqt
    ```

=== "conda"

    ```bash
    conda install -c conda-forge superqt
    ```

Components are tested on:

- macOS, Windows, & Linux
- Python 3.11 and above
- PyQt5 (5.11 and above) & PyQt6
- PySide6

## Widgets

<div class="sq-gallery" markdown>
{{ card("widgets/qrangeslider.md", "QRangeSlider", "Multi-handle slider") }}
{{ card("widgets/qlabeledrangeslider.md", "QLabeledRangeSlider", "`QRangeSlider` variant, with editable labels for each handle") }}
{{ card("widgets/qsearchablecombobox.md", "QSearchableComboBox", "`QComboBox` variant that filters available options based on text input") }}
{{ card("widgets/qcolormap.md", "QColormapComboBox", "`QComboBox` to select from a specified set of colormaps.") }}
{{ card("widgets/qcollapsible.md", "QCollapsible", "A collapsible widget to hide and unhide child widgets.") }}
{{ card("widgets/qtoggleswitch.md", "QToggleSwitch", "`QAbstractButton` that represents a boolean value with a toggle switch.") }}
</div>

[All widgets](widgets/index.md){ .md-button }

## Utilities

See the [Utilities](utilities/index.md) page for font icons, threading tools,
throttling and debouncing, and more.
