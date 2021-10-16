# type: ignore
from . import API_NAME, _get_qtmodule

_QtWidgets = _get_qtmodule(__name__)
globals().update(_QtWidgets.__dict__)


def exec_(self):
    self.exec()


QApplication = _QtWidgets.QApplication
QApplication.exec_ = exec_

# backwargs compat with qt5
if "6" in API_NAME:
    _QtGui = _get_qtmodule("QtGui")
    QAction = _QtGui.QAction
    QShortcut = _QtGui.QShortcut
