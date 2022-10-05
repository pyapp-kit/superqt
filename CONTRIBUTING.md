# Contributing to this repository

This repository seeks to accumulate Qt-based widgets for python (PyQt & PySide)
that are not provided in the native QtWidgets module.

## Clone

To get started fork this repository, and clone your fork:

```bash
# clone your fork
git clone https://github.com/<your_organization>/superqt
cd superqt

# install pre-commit hooks
pre-commit install

# install in editable mode
pip install -e .[dev]

# run tests & make sure everything is working!
pytest
```

## Targeted platforms

All widgets must be well-tested, and should work on:

- Python 3.7 and above
- PyQt5 (5.11 and above) & PyQt6
- PySide2 (5.11 and above) & PySide6
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

Tests can be run in the current environment with `pytest`.  Or, to run tests
against all supported python & Qt versions, run `tox`.
