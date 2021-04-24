# PyQRangeSlider

[![License](https://img.shields.io/pypi/l/PyQRangeSlider.svg?color=green)](https://github.com/tlambert03/PyQRangeSlider/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/PyQRangeSlider.svg?color=green)](https://pypi.org/project/PyQRangeSlider)
[![Python Version](https://img.shields.io/pypi/pyversions/PyQRangeSlider.svg?color=green)](https://python.org)
[![Test](https://github.com/tlambert03/PyQRangeSlider/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/tlambert03/PyQRangeSlider/actions/workflows/test_and_deploy.yml)
[![codecov](https://codecov.io/gh/tlambert03/PyQRangeSlider/branch/master/graph/badge.svg)](https://codecov.io/gh/tlambert03/PyQRangeSlider)

Multi-handle range slider widget for PyQt/PySide

The goal of this package is to provide a QRangeSlider that feels as "native"
as possible.  Styles should match the OS by default, and the slider should
behave like a standard QSlider... just with multiple handles.

- Supports more than 2 handles (e.g. `slider.setValue([0, 10, 60, 80])`)
- Attempts to match QSlider API as closely as possible
- Uses platform-specific styles (for handle, groove, & ticks) but also supports QSS style sheets.
- Supports mouse wheel and keypress (soon) events
- Supports PyQt5, PyQt6, PySide2 and PySide6


## Installation

You can install `PyQRangeSlider` via pip:

    pip install pyqrangeslider


## Issues

If you encounter any problems, please [file an issue] along with a detailed description.


[file an issue]: https://github.com/tlambert03/PyQRangeSlider/issues
