import pdb  # noqa
import sys
from types import FrameType
from typing import Optional

from superqt.qtcompat import QtCore
from superqt.qtcompat.QtWidgets import QApplication


class QtPdb(pdb.Pdb):
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
            print("exit")
            app.exit()
        super().set_quit()


def qt_set_trace(*, header: Optional[str] = None) -> None:
    pdb = QtPdb()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back)


def install_qtbreakpoint() -> None:
    sys.breakpointhook = qt_set_trace


def uninstall_qtbreakpoint() -> None:
    sys.breakpointhook = sys.__breakpointhook__
