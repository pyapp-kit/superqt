# ![tiny](https://user-images.githubusercontent.com/1609449/120636353-8c3f3800-c43b-11eb-8732-a14dec578897.png)  superqt!


[![License](https://img.shields.io/pypi/l/superqt.svg?color=green)](https://github.com/napari/superqt/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/superqt.svg?color=green)](https://pypi.org/project/superqt)
[![Python
Version](https://img.shields.io/pypi/pyversions/superqt.svg?color=green)](https://python.org)
[![Test](https://github.com/napari/superqt/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/napari/superqt/actions/workflows/test_and_deploy.yml)
[![codecov](https://codecov.io/gh/napari/superqt/branch/main/graph/badge.svg?token=dcsjgl1sOi)](https://codecov.io/gh/napari/superqt)

###  "missing" widgets and components for PyQt/PySide

This repository aims to provide high-quality community-contributed Qt widgets and components for PyQt & PySide
that are not provided in the native QtWidgets module.

Components are tested on:

- macOS, Windows, & Linux
- Python 3.7 and above
- PyQt5 (5.11 and above) & PyQt6
- PySide2 (5.11 and above) & PySide6

## Widgets

Widgets include:

- [Float Slider](docs/sliders.md#float-slider)

- [Range Slider](docs/sliders.md#range-slider) (multi-handle slider)

<img src="https://raw.githubusercontent.com/napari/superqt/main/docs/images/demo_darwin10.png" alt="range sliders" width=680>


- [Labeled Sliders](docs/sliders.md#labeled-sliders) (sliders with linked
  spinboxes)

<img src="https://raw.githubusercontent.com/napari/superqt/main/docs/images/labeled_qslider.png" alt="range sliders" width=680>

<img src="https://raw.githubusercontent.com/napari/superqt/main/docs/images/labeled_range.png" alt="range sliders" width=680>

- Unbound Integer SpinBox (backed by python `int`)

## Contributing

We welcome contributions!

Please see the [Contributing Guide](CONTRIBUTING.md)
