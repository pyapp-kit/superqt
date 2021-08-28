from . import API_NAME, _get_submodule

globals().update(_get_submodule(__name__).__dict__)

if "PyQt" in API_NAME:
    Property = globals()["pyqtProperty"]
    Signal = globals()["pyqtSignal"]
    Slot = globals()["pyqtSlot"]
