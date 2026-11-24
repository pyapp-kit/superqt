# QColormapLineEdit

A [`QLineEdit`](https://doc.qt.io/qt-6/qlineedit.html) that shows the colormap
named by its text, as you type: a swatch next to the name, or, if
`fractional_colormap_width` is more than 0.75, behind it. When the text isn't the
name of a colormap in the [cmap catalog](https://cmap-docs.readthedocs.io/en/latest/catalog/),
it shows a fallback colormap (gray, by default), and a question mark icon next to
the name (unless the swatch is behind it). It's the
line edit of [`QColormapComboBox`](qcolormap.md) and
[`CmapCatalogComboBox`](colormap_catalog.md).

!!! note "Requires cmap"

    Colormaps come from the [cmap](https://cmap-docs.readthedocs.io/) library,
    which you can install with the `cmap` extra:

    ```bash
    pip install "superqt[cmap]"
    ```

{{ show_widget() }}

```python
--8<--
examples/qcolormaplineedit.py
--8<--
```

With `allow_invalid=False`, text that isn't a colormap is replaced when editing
finishes: by the first completion of the line edit's completer, if it has one,
or else by the last valid colormap.

{{ show_members('superqt.cmap.QColormapLineEdit') }}
