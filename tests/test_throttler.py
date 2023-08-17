from unittest.mock import Mock

import pytest
from qtpy.QtCore import QObject, Signal

from superqt.utils import qdebounced, qthrottled


def test_debounced(qtbot):
    mock1 = Mock()
    mock2 = Mock()

    @qdebounced(timeout=5)
    def f1() -> str:
        mock1()

    def f2() -> str:
        mock2()

    for _ in range(10):
        f1()
        f2()

    qtbot.wait(5)
    mock1.assert_called_once()
    assert mock2.call_count == 10


def test_throttled(qtbot):
    mock1 = Mock()
    mock2 = Mock()

    @qthrottled(timeout=5)
    def f1() -> str:
        mock1()

    def f2() -> str:
        mock2()

    for _ in range(10):
        f1()
        f2()

    qtbot.wait(5)
    assert mock1.call_count == 2
    assert mock2.call_count == 10


@pytest.mark.parametrize("deco", [qthrottled, qdebounced])
def test_ensure_throttled_sig_inspection(deco, qtbot):
    mock = Mock()

    class Emitter(QObject):
        sig = Signal(int, int, int)

    @deco
    def func(a: int, b: int):
        """docstring"""
        mock(a, b)

    obj = Emitter()
    obj.sig.connect(func)

    # this is the crux of the test...
    # we emit 3 args, but the function only takes 2
    # this should normally work fine in Qt.
    # testing here that the decorator doesn't break it.
    with qtbot.waitSignal(func.triggered, timeout=1000):
        obj.sig.emit(1, 2, 3)
    mock.assert_called_once_with(1, 2)
    assert func.__doc__ == "docstring"
    assert func.__name__ == "func"
