from typing import TYPE_CHECKING

from . import API_NAME, _get_qtmodule

if TYPE_CHECKING:
    from PyQt5.QtWidgets import *  # noqa: F401
    from PyQt6.QtWidgets import *  # noqa: F401
    from PySide2.QtWidgets import *  # noqa: F401
    from PySide6.QtWidgets import *  # noqa: F401


_QtWidgets = _get_qtmodule(__name__, globals())


def exec_(self):
    self.exec()


_QtWidgets.QApplication.exec_ = exec_

# backwargs compat with qt5
if "6" in API_NAME:
    _QtGui = _get_qtmodule("QtGui")
    QAction = _QtGui.QAction  # type: ignore
    QShortcut = _QtGui.QShortcut  # type: ignore
