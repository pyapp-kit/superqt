---
hide:
  - navigation
  - toc
---

<div class="sq-hero" markdown>
<div class="sq-hero__text" markdown>

# ![](images/logo.svg#only-light){ .sq-logo }![](images/logo-dark.svg#only-dark){ .sq-logo } superqt

<p class="sq-lead">"Missing" widgets and components for PyQt and PySide.</p>

superqt is a collection of Qt widgets and utilities that the `QtWidgets` module
doesn't provide: range sliders, sliders for floats, searchable combo boxes and
lists, collapsible sections, font and SVG icons, tools for threading and for
throttling signals, and more. It is built on
[qtpy](https://github.com/spyder-ide/qtpy), so the same code works with PyQt5,
PyQt6, and PySide6.

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

superqt doesn't install a Qt binding. If your environment doesn't have one yet,
install one with an extra:

```bash
pip install "superqt[pyqt6]"  # or [pyqt5], or [pyside6]
```

Some features need extra dependencies, which can also be installed as extras:

| Extra | Installs | Needed for |
| --- | --- | --- |
| `cmap` | [cmap](https://cmap-docs.readthedocs.io/) | [`QColormapComboBox`](widgets/qcolormap.md), [`CmapCatalogComboBox`](widgets/colormap_catalog.md), [colormap utilities](utilities/cmap.md) |
| `quantity` | [pint](https://pint.readthedocs.io/) | [`QQuantity`](widgets/qquantity.md) |
| `iconify` | [pyconify](https://github.com/pyapp-kit/pyconify) | [`QIconifyIcon`](utilities/icons/iconify.md) |
| `font-fa5`, `font-fa6` | Font Awesome 5 or 6 | [font icons](utilities/icons/fonticon.md) |
| `font-mi6`, `font-mi7` | Material Design Icons 6 or 7 | [font icons](utilities/icons/fonticon.md) |

superqt is tested on macOS, Windows, and Linux, with Python 3.11 and later, and
with PyQt5 (5.15), PyQt6, and PySide6.

## Widgets

<div class="sq-gallery sq-gallery--center" markdown>
{{ card("widgets/qrangeslider.md", "QRangeSlider", "A slider with two or more handles, to select a range.") }}
{{ card("widgets/qlabeledrangeslider.md", "QLabeledRangeSlider", "A range slider with editable labels for its handles and range.") }}
{{ card("widgets/qsearchablecombobox.md", "QSearchableComboBox", "A combo box that filters its items as you type.") }}
{{ card("widgets/qlabeledslider.md", "QLabeledSlider", "A slider with an editable label for its value.") }}
{{ card("widgets/qcolormap.md", "QColormapComboBox", "A combo box for choosing a colormap.") }}
{{ card("widgets/qcollapsible.md", "QCollapsible", "A frame that hides or shows its contents when its header is clicked.") }}
{{ card("widgets/qtoggleswitch.md", "QToggleSwitch", "A checkable button drawn as a toggle switch.") }}
{{ card("widgets/qflowlayout.md", "QFlowLayout", "A layout that wraps its items onto new rows to fit the width.") }}
{{ card("widgets/qquantity.md", "QQuantity", "A magnitude and a unit, backed by pint.") }}
{{ card("widgets/qcolorcombobox.md", "QColorComboBox", "A combo box for choosing a color.") }}
{{ card("widgets/qenumcombobox.md", "QEnumComboBox", "A combo box with the members of an `Enum`.") }}
{{ card("widgets/qelidinglabel.md", "QElidingLabel", "A label that shortens its text with an ellipsis to fit.") }}
</div>

[All widgets](widgets/index.md){ .md-button }

## Utilities

The utilities include icons from icon fonts and from Iconify, decorators and
workers for running code in other threads, throttling and debouncing of
functions and signals, syntax highlighting, and context managers for blocking
signals, capturing Qt's log messages, and showing exceptions in a dialog.

<div class="sq-gallery sq-gallery--center" markdown>
{{ card("utilities/code_syntax_highlight.md", "CodeSyntaxHighlight", "Syntax highlighting for code in a text edit, with Pygments.") }}
{{ card("utilities/icons/iconify.md", "QIconifyIcon", "Any of Iconify's 450,000+ SVG icons, as a QIcon.") }}
{{ card("utilities/throttling.md", "qthrottled, qdebounced", "Decorators that limit how often a function runs when it's called rapidly.") }}
</div>

[All utilities](utilities/index.md){ .md-button }
