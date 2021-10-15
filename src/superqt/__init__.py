"""superqt is a collection of QtWidgets for python."""
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._eliding_label import QElidingLabel
from .combobox import QEnumComboBox
from .sliders import (
    QDoubleRangeSlider,
    QDoubleSlider,
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
    QRangeSlider,
)
from .spinbox import QLargeIntSpinBox
from .utils import QMessageHandler, ensure_main_thread, ensure_object_thread

__all__ = [
    "ensure_main_thread",
    "ensure_object_thread",
    "QDoubleRangeSlider",
    "QDoubleSlider",
    "QElidingLabel",
    "QLabeledDoubleRangeSlider",
    "QLabeledDoubleSlider",
    "QLabeledRangeSlider",
    "QLabeledSlider",
    "QLargeIntSpinBox",
    "QMessageHandler",
    "QRangeSlider",
    "QEnumComboBox",
    # provided by *all* backends in qtcompat via __getattr__ below
    "QtGui",
    "QtWidgets",
    "QtCore",
    "QtHelp",
    "QtNetwork",
    "QtOpenGL",
    "QtPrintSupport",
    "QtQml",
    "QtQuick",
    "QtQuickWidgets",
    "QtSql",
    "QtSvg",
    "QtTest",
    "QtXml",
]


# Allow any imports from PySide/PyQt via qtcompat...
def __getattr__(name: str):
    err = f"module {__name__!r} has no attribute {name!r}"
    if name.startswith("Qt"):
        import importlib

        try:
            return importlib.import_module(f"{__package__}.qtcompat.{name}")
        except ImportError:
            err += f". Also looked in '{__package__}.qtcompat'"
    raise AttributeError(err)
