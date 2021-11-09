import pdb  # noqa
import sys
from types import FrameType
from typing import Optional

from superqt.qtcompat import QtCore
from superqt.qtcompat.QtWidgets import QApplication


class _QtPdb(pdb.Pdb):
    def set_trace(self, frame: Optional[FrameType] = None) -> None:
        QApplication.processEvents()
        if hasattr(QtCore, "pyqtRemoveInputHook"):
            QtCore.pyqtRemoveInputHook()
        super().set_trace(frame)

    def set_continue(self) -> None:
        super().set_continue()
        if hasattr(QtCore, "pyqtRestoreInputHook"):
            QtCore.pyqtRestoreInputHook()

    def set_quit(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.exit()
        super().set_quit()


def qt_set_trace(*, header: Optional[str] = None) -> None:
    """Enter the debugger at the calling stack frame, with Qt event loop removed.

    This is useful to hard-code a breakpoint at a given point in a program,
    even if the code is not otherwise being debugged (e.g. when an assertion fails).
    If given, header is printed to the console just before debugging begins.
    """
    pdb = _QtPdb()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)


def install_qt_breakpoint() -> None:
    """Install `qt_set_trace` as the default breakpointhook.

    This lets you use the builtin `breakpoint()` anywhere in your Qt code.
    """
    sys.breakpointhook = qt_set_trace


def uninstall_qt_breakpoint() -> None:
    """Uninstall `qt_set_trace` as the default breakpointhook."""
    sys.breakpointhook = sys.__breakpointhook__
