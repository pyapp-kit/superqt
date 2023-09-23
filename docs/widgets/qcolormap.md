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

```python
from cmap import Colormap
from qtpy.QtWidgets import QApplication

from superqt import QColormapComboBox

app = QApplication([])

cmap_combo = QColormapComboBox()
# see note above about colormap-like objects
# as names from the cmap catalog
cmap_combo.addColormaps(["viridis", "plasma", "magma", "gray"])
# as a sequence of colors, linearly interpolated
cmap_combo.addColormap(("#0f0", "slateblue", "#F3A003A0"))
# as a `cmap.Colormap` instance with custom name:
cmap_combo.addColormap(Colormap(("green", "white", "orange"), name="MyMap"))

cmap_combo.show()
app.exec()
```

{{ show_widget(200) }}

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
