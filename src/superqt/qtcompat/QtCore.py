from . import _get_submodule
from ._util import ScopedEnumMeta

name_changes = {
    "PyQt": {
        "Property": "pyqtProperty",
        "Signal": "pyqtSignal",
        "SignalInstance": "pyqtBoundSignal",
        "Slot": "pyqtSlot",
        "__version__": "QT_VERSION_STR",
    }
}
_QtCore = _get_submodule(__name__, globals(), name_changes)


class Qt(metaclass=ScopedEnumMeta):
    ...


del _get_submodule, ScopedEnumMeta, name_changes
