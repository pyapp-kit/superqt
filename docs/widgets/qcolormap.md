# QColormapComboBox

`QComboBox` variant to select from a specific set of colormaps.

!!! note "requires cmap"

    This widget uses the [cmap](https://cmap-docs.readthedocs.io/) library
    to provide colormaps.  You can install it with:

    ```shell
    # use the `cmap` extra to include colormap support
    pip install superqt[cmap]
    ```

### ColorMapLike objects

Colormaps may be specified in a variety of ways, such as by name (string), an iterable of a color/color-like objects, or as
a [`cmap.Colormap`][] instance. See [cmap documentation for details on
all ColormapLike types](https://cmap-docs.readthedocs.io/en/latest/colormaps/#colormaplike-objects)

### Example

{{ show_widget() }}

```python
--8<--
examples/qcolormap.py
--8<--
```

### Style Customization

Note that both the LineEdit and the dropdown can be styled to have the colormap
on the left, or fill the entire width of the widget.

To make the CombBox label colormap fill the entire width of the widget:

```python
from superqt.cmap import QColormapLineEdit

cmap_combo.setLineEdit(QColormapLineEdit())
```

To make the CombBox dropdown colormaps fill
less than the entire width of the widget:

```python
from superqt.cmap import QColormapItemDelegate

delegate = QColormapItemDelegate(fractional_colormap_width=0.33)
cmap_combo.setItemDelegate(delegate)
```

{{ show_members('superqt.QColormapComboBox') }}
