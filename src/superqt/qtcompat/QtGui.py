# type: ignore
from . import API_NAME, _get_qtmodule

_QtGui = _get_qtmodule(__name__)
globals().update(_QtGui.__dict__)

if "6" in API_NAME:

    def pos(self, *a):
        _pos = self.position(*a)
        return _pos.toPoint()

    _QtGui.QMouseEvent.pos = pos
