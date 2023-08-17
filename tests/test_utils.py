from unittest.mock import Mock

from qtpy.QtCore import QObject, Signal

from superqt.utils import signals_blocked
from superqt.utils._util import get_max_args


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


def test_get_max_args_simple():
    def fun1():
        pass

    assert get_max_args(fun1) == 0

    def fun2(a):
        pass

    assert get_max_args(fun2) == 1

    def fun3(a, b=1):
        pass

    assert get_max_args(fun3) == 2

    def fun4(a, *, b=2):
        pass

    assert get_max_args(fun4) == 1

    def fun5(a, *b):
        pass

    assert get_max_args(fun5) is None
    
    assert get_max_args(print) is None


def test_get_max_args_wrapped():
    from functools import partial, wraps

    def fun1(a, b):
        pass

    assert get_max_args(partial(fun1, 1)) == 1

    def dec(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)

        return wrapper

    assert get_max_args(dec(fun1)) == 2


def test_get_max_args_methods():
    class A:
        def fun1(self):
            pass

        def fun2(self, a):
            pass

        def __call__(self, a, b=1):
            pass

    assert get_max_args(A().fun1) == 0
    assert get_max_args(A().fun2) == 1
    assert get_max_args(A()) == 2
