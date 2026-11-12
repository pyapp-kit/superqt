# QIconifyIcon

A `QIcon` with an SVG icon from [Iconify](https://iconify.design/), which
collects the icons of many open source icon sets (Bootstrap, Font Awesome,
Material Design, and many others). Icons are downloaded when they're first used
(with [pyconify](https://github.com/pyapp-kit/pyconify)), and cached on disk.
Unlike [font icons](fonticon.md), they don't need a package for each icon set.

!!! note "Requires pyconify"

    Install [pyconify](https://github.com/pyapp-kit/pyconify) with the `iconify`
    extra:

    ```bash
    pip install "superqt[iconify]"
    ```

Search for icons at <https://icon-sets.iconify.design>, and create one with its
key, in the form `"prefix:name"`: `QIconifyIcon("bi:bell")`. Icons can also be
colored, flipped, and rotated, and `addKey` adds icons for other modes and states
of the same `QIcon`.

## Example

{{ show_widget() }}

```python
--8<--
examples/iconify.py
--8<--
```

::: superqt.QIconifyIcon
    options:
      heading_level: 2
