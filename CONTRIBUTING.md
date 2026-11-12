# Contributing to this repository

This repository seeks to accumulate Qt-based widgets for python (PyQt & PySide)
that are not provided in the native QtWidgets module.

## Clone

To get started fork this repository, and clone your fork:

```bash
# clone your fork
git clone https://github.com/<your_organization>/superqt
cd superqt

# create an environment with the dev dependencies, and PyQt6 as the Qt backend
uv sync --extra pyqt6

# install the pre-commit hooks
uv run prek install

# run tests & make sure everything is working!
uv run pytest
```

## Targeted platforms

All widgets must be well-tested, and should work on:

- Python 3.11 and above
- PyQt5 (5.15) & PyQt6
- PySide6
- macOS, Windows, & Linux


## Style Guide

All widgets should try to match the native Qt API as much as possible:

- Methods should use `camelCase` naming.
- Getters/setters use the `attribute()/setAttribute()` pattern.
- Private methods should use `_camelCaseNaming`.
- `__init__` methods should be like Qt constructors, meaning they often don't
  include parameters for most of the widgets properties.
- When possible, widgets should inherit from the most similar native widget
  available. It should strictly match the Qt API where it exists, and attempt to
  cover as much of the native API as possible; this includes properties, public
  functions, signals, and public slots.

## Testing

Tests can be run in the current environment with `uv run pytest`.

## Documentation

The documentation is built with [Zensical](https://zensical.org). Widget
screenshots and animations are rendered from the runnable scripts in
`docs/examples/` in a separate step, before building (outputs are cached, so
reruns only render what changed):

```bash
uv run --group docs python docs/_gen_media.py  # renders into docs/_generated/
uv run --group docs zensical serve             # preview at http://localhost:8000
```

To document a new widget:

1. Add a runnable example, `docs/examples/<name>.py`, that shows one window.
2. Add a page, `docs/widgets/<name>.md`, that shows the example with
   `{{ show_widget() }}`, includes its code with a (block-style) snippet in a
   `python` code block, and lists its API with
   `{{ show_members("superqt.<Class>") }}` (see the other pages). Add the page
   to `nav` in `zensical.toml`, and a `card` for it in `docs/widgets/index.md`.
3. Optionally, set the window size or record an animation in `docs/_scenes.py`.
