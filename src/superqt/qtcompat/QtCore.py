from typing import TYPE_CHECKING

from . import API_NAME, _get_qtmodule

if TYPE_CHECKING:
    from PyQt5.QtCore import *  # noqa: F401
    from PyQt6.QtCore import *  # noqa: F401
    from PySide2.QtCore import *  # noqa: F401
    from PySide6.QtCore import *  # noqa: F401


_QtCore = _get_qtmodule(__name__, globals())
if "PyQt" in API_NAME:
    Property = _QtCore.pyqtProperty  # type: ignore
    Signal = _QtCore.pyqtSignal  # type: ignore
    SignalInstance = getattr(_QtCore, "pyqtBoundSignal", None)  # type: ignore
    Slot = _QtCore.pyqtSlot  # type: ignore
    __version__ = _QtCore.QT_VERSION_STR


# from superqt.qtcompat._util import ScopedEnumMeta

# class Qt(metaclass=ScopedEnumMeta):
#     ...

# del _get_qtmodule, ScopedEnumMeta
