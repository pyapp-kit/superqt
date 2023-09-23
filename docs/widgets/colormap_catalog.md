# CmapCatalogComboBox

Searchable `QComboBox` variant that contains the
[entire cmap colormap catalog](https://cmap-docs.readthedocs.io/en/latest/catalog/)

!!! note "requires cmap"

    This widget uses the [cmap](https://cmap-docs.readthedocs.io/) library
    to provide colormaps.  You can install it with:

    ```shell
    # use the `cmap` extra to include colormap support
    pip install superqt[cmap]
    ```

You can limit the colormaps shown by setting the `categories` or
`interpolation` keyword arguments.

```python
from qtpy.QtWidgets import QApplication

from superqt.cmap import CmapCatalogComboBox

app = QApplication([])

catalog_combo = CmapCatalogComboBox(interpolation="linear")
catalog_combo.setCurrentText("viridis")
catalog_combo.show()

app.exec()
```

{{ show_widget(130) }}

{{ show_members('superqt.cmap.CmapCatalogComboBox') }}
