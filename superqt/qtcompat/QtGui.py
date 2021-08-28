"""
Modified from qtpy.QtGui
Provides QtGui classes and functions.
"""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtGui import *
elif PYSIDE2:
    from PySide2.QtGui import *
elif PYQT6:
    from PyQt6.QtGui import *

    def pos(self, *a):
        _pos = self.position(*a)
        return _pos.toPoint()

    QMouseEvent.pos = pos

elif PYSIDE6:
    from PySide6.QtGui import *  # noqa
else:
    raise PythonQtError("No Qt bindings could be found")
