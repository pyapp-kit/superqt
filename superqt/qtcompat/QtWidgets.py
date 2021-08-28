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
    from PyQt6.QtGui import QAction  # noqa TODO: warn?
    from PyQt6.QtWidgets import *


elif PYSIDE6:
    from PySide6.QtGui import QAction  # noqa  TODO: warn?
    from PySide6.QtWidgets import *  # noqa

else:
    raise PythonQtError("No Qt bindings could be found")


def exec_(self):
    self.exec()


QApplication.exec_ = exec_
