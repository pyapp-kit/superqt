import gc
import weakref
from unittest.mock import Mock

import pytest
from qtpy.QtCore import QObject, Signal

from superqt.utils import qdebounced, qthrottled
from superqt.utils._throttler import ThrottledCallable


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


@pytest.mark.usefixtures("qapp")
def test_stop_timer_simple():
    mock = Mock()

    @qdebounced(timeout=5)
    def f1() -> str:
        mock()

    f1()
    assert f1._timer.isActive()
    mock.assert_not_called()
    f1.flush(restart_timer=False)
    assert not f1._timer.isActive()
    mock.assert_called_once()


@pytest.mark.usefixtures("qapp")
def test_stop_timer_no_event_pending():
    mock = Mock()

    @qdebounced(timeout=5)
    def f1() -> str:
        mock()

    f1()
    assert f1._timer.isActive()
    mock.assert_not_called()
    f1.flush()
    assert f1._timer.isActive()
    mock.assert_called_once()
    f1.flush(restart_timer=False)
    assert not f1._timer.isActive()
    mock.assert_called_once()


def test_debouncer_method(qtbot):
    class A(QObject):
        def __init__(self):
            super().__init__()
            self.count = 0

        def callback(self):
            self.count += 1

    a = A()
    assert all(not isinstance(x, ThrottledCallable) for x in a.children())
    b = qdebounced(a.callback, timeout=4)
    assert any(isinstance(x, ThrottledCallable) for x in a.children())
    for _ in range(10):
        b()

    qtbot.wait(5)

    assert a.count == 1


def test_debouncer_method_definition(qtbot):
    mock1 = Mock()
    mock2 = Mock()

    class A(QObject):
        def __init__(self):
            super().__init__()
            self.count = 0

        @qdebounced(timeout=4)
        def callback(self):
            self.count += 1

        @qdebounced(timeout=4)
        @staticmethod
        def call1():
            mock1()

        @staticmethod
        @qdebounced(timeout=4)
        def call2():
            mock2()

    a = A()
    assert all(not isinstance(x, ThrottledCallable) for x in a.children())
    for _ in range(10):
        a.callback(1)
        A.call1(34)
        a.call1(22)
        a.call2(22)
        A.call2(32)

    qtbot.wait(5)
    assert a.count == 1
    mock1.assert_called_once()
    mock2.assert_called_once()


def test_class_with_slots(qtbot):
    class A:
        __slots__ = ("__weakref__", "count")

        def __init__(self):
            self.count = 0

        @qdebounced(timeout=4)
        def callback(self):
            self.count += 1

    a = A()
    for _ in range(10):
        a.callback()

    qtbot.wait(5)
    assert a.count == 1


@pytest.mark.usefixtures("qapp")
def test_class_with_slots_except():
    class A:
        __slots__ = ("count",)

        def __init__(self):
            self.count = 0

        @qdebounced(timeout=4)
        def callback(self):
            self.count += 1

    with pytest.raises(TypeError, match="To use qthrottled or qdebounced"):
        A().callback()


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


def test_qthrottled_does_not_prevent_gc(qtbot):
    mock = Mock()

    class Thing:
        @qdebounced(timeout=1)
        def dmethod(self) -> None:
            mock()

        @qthrottled(timeout=1)
        def tmethod(self, x: int = 1) -> None:
            mock()

    thing = Thing()
    thing_ref = weakref.ref(thing)
    assert thing_ref() is not None
    thing.dmethod()
    qtbot.waitUntil(thing.dmethod._future.done, timeout=2000)
    assert mock.call_count == 1
    thing.tmethod()
    qtbot.waitUntil(thing.tmethod._future.done, timeout=2000)
    assert mock.call_count == 2

    wm = thing.tmethod
    assert isinstance(wm, ThrottledCallable)
    del thing
    gc.collect()
    assert thing_ref() is None

    with pytest.warns(RuntimeWarning, match="Method has been garbage collected"):
        wm()
        wm._set_future_result()
