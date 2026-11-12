# QColormapComboBox

A [`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) for choosing a colormap
from a list. Each item shows the colormap, and `currentColormap()` returns a
[`cmap.Colormap`][].

!!! note "Requires cmap"

    Colormaps come from the [cmap](https://cmap-docs.readthedocs.io/) library,
    which you can install with the `cmap` extra:

    ```bash
    pip install "superqt[cmap]"
    ```

Colormaps can be added in any of the forms that cmap accepts: the name of a
colormap in its catalog, a sequence of colors (which are interpolated), a
`cmap.Colormap`, and [others](https://cmap-docs.readthedocs.io/en/latest/colormaps/#colormaplike-objects).

- Typing in the combo box filters the colormaps (turn this off with
  `setFilterable(False)`).
- With `setUserAdditionsAllowed(True)` (or `allow_user_colormaps=True`), an
  "Add Colormap..." item at the end of the list opens a dialog for choosing any
  colormap in the [cmap catalog](https://cmap-docs.readthedocs.io/en/latest/catalog/).
- Right-clicking an item in the list shows a menu for removing it.

## Example

{{ show_widget() }}

```python
--8<--
examples/qcolormap.py
--8<--
```

## Customizing the appearance

By default, the colormap fills about a third of the combo box, next to its name,
and all of the width of the items in the list. Both can be changed.

To make the colormap fill the whole width of the combo box:

```python
cmap_combo.lineEdit().setFractionalColormapWidth(1)
```

To make the colormaps in the list fill a third of their width:

```python
from superqt.cmap import QColormapItemDelegate

delegate = QColormapItemDelegate(fractional_colormap_width=0.33)
cmap_combo.setItemDelegate(delegate)
```

{{ show_members('superqt.QColormapComboBox') }}
