# type: ignore
from . import API_NAME, _get_qtmodule

_QtCore = _get_qtmodule(__name__)
globals().update(_QtCore.__dict__)

if "PyQt" in API_NAME:
    Property = _QtCore.pyqtProperty
    Signal = _QtCore.pyqtSignal
    SignalInstance = getattr(_QtCore, "pyqtBoundSignal", None)
    Slot = _QtCore.pyqtSlot
    __version__ = _QtCore.QT_VERSION_STR
