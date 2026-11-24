# QIconifyIcon

A `QIcon` with one of the SVG icons of [Iconify](https://iconify.design/): over
450,000 icons, from more than 260 open source icon sets. Find an icon at
<https://icon-sets.iconify.design>, and create it with its key, in the form
`"prefix:name"`: `QIconifyIcon("bi:bell")`. (For a comparison with font icons,
see [Icons](index.md#comparison).)

!!! note "Requires pyconify"

    Icons are downloaded with [pyconify](https://github.com/pyapp-kit/pyconify),
    which you can install with the `iconify` extra:

    ```bash
    pip install "superqt[iconify]"
    ```

## Example

{{ show_widget() }}

```python
--8<--
examples/iconify.py
--8<--
```

## Colors, rotation, and states

Single-color icons can be colored, and any icon can be flipped or rotated:

```python
--8<--
examples/iconify_color.py:icon
--8<--
```

{{ show_widget("iconify_color") }}

Without a `color`, single-color icons are black, whatever the widget's palette.
For a dark theme, pass a color, for example one from the palette:

```python
--8<--
examples/iconify_palette.py:icon
--8<--
```

{{ show_widget("iconify_palette") }}

`addKey` adds icons for other states and modes of the same `QIcon`. For
example, a different icon when a checkable button is checked:

```python
--8<--
examples/iconify_states.py:icon
--8<--
```

{{ show_widget("iconify_states") }}

## How icons are fetched

The first time an icon is used, pyconify downloads it from the Iconify API
(`api.iconify.design`), and saves it in a cache on disk, where later sessions
find it.

- The download happens when the `QIconifyIcon` is created, in the thread that
  creates it, which waits for it (with a timeout of 2 seconds).
- The first icon of each session also asks the API when the icon sets last
  changed, so that cached icons that are out of date are downloaded again.
- Without network access, cached icons still load. An icon that isn't cached
  causes a warning, and is replaced by a question mark icon.
- `pyconify.get_cache_directory()` returns the location of the cache. To use
  another directory, set the `PYCONIFY_CACHE` environment variable to it (or to
  `0`, to turn the cache off) before `superqt.iconify` (or pyconify) is imported.

## Using icons offline, or in an app

To make sure that an app's icons are available without network access, ship
them in a cache directory:

1. Fill a directory with the icons: create each of them once (for example, by
   running the app), with `PYCONIFY_CACHE` set to that directory.
2. Ship the directory with the app, and set `PYCONIFY_CACHE` to it before
   importing `superqt.iconify`:

    ```python
    import os
    from pathlib import Path

    os.environ["PYCONIFY_CACHE"] = str(Path(__file__).parent / "icon_cache")

    from superqt import QIconifyIcon
    ```

The icons are then loaded from the directory. With network access, an icon whose
set has changed since is downloaded again, into the same directory (so it should
be writable).

## Licenses

Each icon set has its own license. Most are permissive (such as MIT or Apache
2.0), but many require attribution (CC BY 4.0), and a few are GPL. The license of
a set is shown on its page at <https://icon-sets.iconify.design>, and returned by
`pyconify.collections()`.

## API

::: superqt.QIconifyIcon
    options:
      heading_level: 3
