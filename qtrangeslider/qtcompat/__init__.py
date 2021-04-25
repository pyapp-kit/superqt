# -*- coding: utf-8 -*-
#
# Copyright © 2009- The Spyder Development Team
# Copyright © 2014-2015 Colin Duquesnoy
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
This file is borrowed from qtpy and modified to support PySide6/PyQt6 (drops PyQt4)
"""

import os
import platform
import sys
import warnings
from distutils.version import LooseVersion


class PythonQtError(RuntimeError):
    """Error raise if no bindings could be selected."""


class PythonQtWarning(Warning):
    """Warning if some features are not implemented in a binding."""


# Qt API environment variable name
QT_API = "QT_API"

# Names of the expected PyQt5 api
PYQT5_API = ["pyqt5"]

# Names of the expected PyQt6 api
PYQT6_API = ["pyqt6"]

# Names of the expected PySide2 api
PYSIDE2_API = ["pyside2"]

# Names of the expected PySide6 api
PYSIDE6_API = ["pyside6"]

# Detecting if a binding was specified by the user
binding_specified = QT_API in os.environ

# Setting a default value for QT_API
os.environ.setdefault(QT_API, "pyqt5")

API = os.environ[QT_API].lower()
initial_api = API
assert API in (PYQT5_API + PYQT6_API + PYSIDE2_API + PYSIDE6_API)

PYQT5 = True
PYSIDE2 = PYQT6 = PYSIDE6 = False

# When `FORCE_QT_API` is set, we disregard
# any previously imported python bindings.
if os.environ.get("FORCE_QT_API") is not None:
    if "PyQt5" in sys.modules:
        API = initial_api if initial_api in PYQT5_API else "pyqt5"
    elif "PySide2" in sys.modules:
        API = initial_api if initial_api in PYSIDE2_API else "pyside2"
    elif "PyQt6" in sys.modules:
        API = initial_api if initial_api in PYQT6_API else "pyqt6"
    elif "PySide6" in sys.modules:
        API = initial_api if initial_api in PYSIDE6_API else "pyside6"


if API in PYQT5_API:
    try:
        from PyQt5.QtCore import PYQT_VERSION_STR as PYQT_VERSION  # noqa
        from PyQt5.QtCore import QT_VERSION_STR as QT_VERSION  # noqa

        PYSIDE_VERSION = None  # noqa

        if sys.platform == "darwin":
            macos_version = LooseVersion(platform.mac_ver()[0])
            if macos_version < LooseVersion("10.10"):
                if LooseVersion(QT_VERSION) >= LooseVersion("5.9"):
                    raise PythonQtError(
                        "Qt 5.9 or higher only works in "
                        "macOS 10.10 or higher. Your "
                        "program will fail in this "
                        "system."
                    )
            elif macos_version < LooseVersion("10.11"):
                if LooseVersion(QT_VERSION) >= LooseVersion("5.11"):
                    raise PythonQtError(
                        "Qt 5.11 or higher only works in "
                        "macOS 10.11 or higher. Your "
                        "program will fail in this "
                        "system."
                    )

            del macos_version
    except ImportError:
        API = os.environ["QT_API"] = "pyside2"

if API in PYSIDE2_API:
    try:
        from PySide2 import __version__ as PYSIDE_VERSION  # noqa
        from PySide2.QtCore import __version__ as QT_VERSION  # noqa

        PYQT_VERSION = None  # noqa
        PYQT5 = False
        PYSIDE2 = True

        if sys.platform == "darwin":
            macos_version = LooseVersion(platform.mac_ver()[0])
            if macos_version < LooseVersion("10.11"):
                if LooseVersion(QT_VERSION) >= LooseVersion("5.11"):
                    raise PythonQtError(
                        "Qt 5.11 or higher only works in "
                        "macOS 10.11 or higher. Your "
                        "program will fail in this "
                        "system."
                    )

            del macos_version
    except ImportError:
        API = os.environ["QT_API"] = "pyqt6"

if API in PYQT6_API:
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR as PYQT_VERSION  # noqa
        from PyQt6.QtCore import QT_VERSION_STR as QT_VERSION  # noqa

        PYSIDE_VERSION = None  # noqa
        PYQT5 = False
        PYQT6 = True

    except ImportError:
        API = os.environ["QT_API"] = "pyside6"

if API in PYSIDE6_API:
    try:
        from PySide6 import __version__ as PYSIDE_VERSION  # noqa
        from PySide6.QtCore import __version__ as QT_VERSION  # noqa

        PYQT_VERSION = None  # noqa
        PYQT5 = False
        PYSIDE6 = True

    except ImportError:
        API = None

if API is None:
    raise PythonQtError(
        "No Qt bindings could be found.\nYou must install one of the following packages "
        "to use QtRangeSlider: PyQt5, PyQt6, PySide2, or PySide6"
    )

# If a correct API name is passed to QT_API and it could not be found,
# switches to another and informs through the warning
if API != initial_api and binding_specified:
    warnings.warn(
        'Selected binding "{}" could not be found, '
        'using "{}"'.format(initial_api, API),
        RuntimeWarning,
    )

API_NAME = {
    "pyqt5": "PyQt5",
    "pyqt6": "PyQt6",
    "pyside2": "PySide2",
    "pyside6": "PySide6",
}[API]
