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

{{ show_widget() }}

```python
--8<--
examples/colormap_catalog.py
--8<--
```

{{ show_members('superqt.cmap.CmapCatalogComboBox') }}
