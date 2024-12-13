# ![tiny](https://user-images.githubusercontent.com/1609449/120636353-8c3f3800-c43b-11eb-8732-a14dec578897.png)  superqt!

[![License](https://img.shields.io/pypi/l/superqt.svg?color=green)](https://github.com/pyapp-kit/superqt/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/superqt.svg?color=green)](https://pypi.org/project/superqt)
[![Python
Version](https://img.shields.io/pypi/pyversions/superqt.svg?color=green)](https://python.org)
[![Test](https://github.com/pyapp-kit/superqt/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/pyapp-kit/superqt/actions/workflows/test_and_deploy.yml)
[![codecov](https://codecov.io/gh/pyapp-kit/superqt/branch/main/graph/badge.svg?token=dcsjgl1sOi)](https://codecov.io/gh/pyapp-kit/superqt)

###  "missing" widgets and components for PyQt/PySide

This repository aims to provide high-quality community-contributed Qt widgets and components for PyQt & PySide
that are not provided in the native QtWidgets module.

Components are tested on:

- macOS, Windows, & Linux
- Python 3.9 and above
- PyQt5 (5.11 and above) & PyQt6
- PySide2 (5.11 and above) & PySide6

## Documentation

Documentation is available at https://pyapp-kit.github.io/superqt/

## Widgets

superqt provides a variety of widgets that are not included in the native QtWidgets module, including multihandle (range) sliders, comboboxes, and more.

See the [widgets documentation](https://pyapp-kit.github.io/superqt/widgets) for a full list of widgets.

- [Range Slider](https://pyapp-kit.github.io/superqt/widgets/qrangeslider/) (multi-handle slider)

<img src="https://raw.githubusercontent.com/pyapp-kit/superqt/main/docs/images/demo_darwin10.png" alt="range sliders" width=680>

<img src="https://raw.githubusercontent.com/pyapp-kit/superqt/main/docs/images/labeled_qslider.png" alt="range sliders" width=680>

<img src="https://raw.githubusercontent.com/pyapp-kit/superqt/main/docs/images/labeled_range.png" alt="range sliders" width=680>

## Utilities

superqt includes a number of utilities for working with Qt, including:

- tools and decorators for working with threads in qt.
- `superqt.fonticon` for generating icons from font files (such as [Material Design Icons](https://materialdesignicons.com/) and [Font Awesome](https://fontawesome.com/))

See the [utilities documentation](https://pyapp-kit.github.io/superqt/utilities/) for a full list of utilities.

## Contributing

We welcome contributions!

Please see the [Contributing Guide](CONTRIBUTING.md)
