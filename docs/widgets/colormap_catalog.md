# CmapCatalogComboBox

A [`QComboBox`](https://doc.qt.io/qt-6/qcombobox.html) with every colormap in the
[cmap catalog](https://cmap-docs.readthedocs.io/en/latest/catalog/). Typing in it
shows the colormaps whose names contain the text, and `currentColormap()`
returns a [`cmap.Colormap`][].

!!! note "Requires cmap"

    Colormaps come from the [cmap](https://cmap-docs.readthedocs.io/) library,
    which you can install with the `cmap` extra:

    ```bash
    pip install "superqt[cmap]"
    ```

The `categories` and `interpolation` keyword arguments limit the colormaps to
those in some categories (such as `"sequential"`), or with one interpolation
(such as `"linear"`). By default, colormaps are listed by their short names, and
by their full names (`namespace:name`) only where two namespaces use the same
short name; pass `prefer_short_names=False` to always use full names.

{{ show_widget() }}

```python
--8<--
examples/colormap_catalog.py
--8<--
```

{{ show_members('superqt.cmap.CmapCatalogComboBox') }}
