# type: ignore
from . import API_NAME, _get_qtmodule

_QtWidgets = _get_qtmodule(__name__)
globals().update(_QtWidgets.__dict__)


QApplication = _QtWidgets.QApplication
if not hasattr(QApplication, "exec"):

    def exec_(self):
        _QtWidgets.QApplication.exec(self)

    QApplication.exec = exec_

# backwargs compat with qt5
if "6" in API_NAME:
    _QtGui = _get_qtmodule("QtGui")
    QAction = _QtGui.QAction
    QShortcut = _QtGui.QShortcut
