# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Developmet Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Modified from qtpy.QtWidgets
Provides widget classes and functions.
"""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtWidgets import *
elif PYSIDE2:
    from PySide2.QtWidgets import *
elif PYQT6:
    from PyQt6.QtWidgets import *

    # backwards compat with PyQt5
    # namespace moves:
    for cls in (QStyle, QSlider, QSizePolicy, QSpinBox):
        for attr in dir(cls):
            if not attr[0].isupper():
                continue
            ns = getattr(cls, attr)
            for name, val in vars(ns).items():
                if not name.startswith("_"):
                    setattr(cls, name, val)

    def exec_(self):
        self.exec()

    QApplication.exec_ = exec_

elif PYSIDE6:
    from PySide6.QtWidgets import *  # noqa

else:
    raise PythonQtError("No Qt bindings could be found")
