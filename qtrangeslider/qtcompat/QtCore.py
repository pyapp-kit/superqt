# -*- coding: utf-8 -*-
#
# Copyright © 2014-2015 Colin Duquesnoy
# Copyright © 2009- The Spyder Development Team
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

"""
Modified from qtpy.QtCore.
Provides QtCore classes and functions.
"""

from . import PYQT5, PYQT6, PYSIDE2, PYSIDE6, PythonQtError

if PYQT5:
    from PyQt5.QtCore import QT_VERSION_STR as __version__
    from PyQt5.QtCore import *
    from PyQt5.QtCore import pyqtProperty as Property  # noqa
    from PyQt5.QtCore import pyqtSignal as Signal  # noqa
    from PyQt5.QtCore import pyqtSlot as Slot  # noqa

    # Those are imported from `import *`
    del pyqtSignal, pyqtBoundSignal, pyqtSlot, pyqtProperty, QT_VERSION_STR
elif PYQT6:
    from PyQt6.QtCore import QT_VERSION_STR as __version__
    from PyQt6.QtCore import *
    from PyQt6.QtCore import pyqtProperty as Property  # noqa
    from PyQt6.QtCore import pyqtSignal as Signal  # noqa
    from PyQt6.QtCore import pyqtSlot as Slot  # noqa

    # backwards compat with PyQt5
    # namespace moves:
    for cls in (QEvent, Qt):
        for attr in dir(cls):
            if not attr[0].isupper():
                continue
            ns = getattr(cls, attr)
            for name, val in vars(ns).items():
                if not name.startswith("_"):
                    setattr(cls, name, val)

    # Those are imported from `import *`
    del pyqtSignal, pyqtBoundSignal, pyqtSlot, pyqtProperty, QT_VERSION_STR
elif PYSIDE2:
    import PySide2.QtCore
    from PySide2.QtCore import *  # noqa

    __version__ = PySide2.QtCore.__version__
elif PYSIDE6:
    import PySide6.QtCore
    from PySide6.QtCore import *  # noqa

    __version__ = PySide6.QtCore.__version__

else:
    raise PythonQtError("No Qt bindings could be found")
