from typing import TYPE_CHECKING

from . import API_NAME, _get_qtmodule

if TYPE_CHECKING:
    from PyQt5.QtGui import *  # noqa: F401
    from PyQt6.QtGui import *  # noqa: F401
    from PySide2.QtGui import *  # noqa: F401
    from PySide6.QtGui import *  # noqa: F401


_QtGui = _get_qtmodule(__name__, globals())


if "6" in API_NAME:

    def pos(self, *a):
        _pos = self.position(*a)
        return _pos.toPoint()

    _QtGui.QMouseEvent.pos = pos
