from unittest.mock import Mock

from qtpy.QtCore import QObject, Signal

from superqt.utils import signals_blocked


def test_signal_blocker(qtbot):
    """make sure context manager signal blocker works"""

    class Emitter(QObject):
        sig = Signal()

    obj = Emitter()
    receiver = Mock()
    obj.sig.connect(receiver)

    # make sure signal works
    with qtbot.waitSignal(obj.sig):
        obj.sig.emit()

    receiver.assert_called_once()
    receiver.reset_mock()

    with signals_blocked(obj):
        obj.sig.emit()
        qtbot.wait(10)

    receiver.assert_not_called()
