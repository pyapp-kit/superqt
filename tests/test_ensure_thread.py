import inspect
import os
import threading
import time
from concurrent.futures import Future, TimeoutError
from functools import wraps
from unittest.mock import Mock

import pytest
from qtpy.QtCore import QCoreApplication, QObject, QThread, Signal

from superqt.utils import ensure_main_thread, ensure_object_thread

skip_on_ci = pytest.mark.skipif(bool(os.getenv("CI")), reason="github hangs")


class SampleObject(QObject):
    assigment_done = Signal()

    def __init__(self):
        super().__init__()
        self.main_thread_res = {}
        self.object_thread_res = {}
        self.main_thread_prop_val = None
        self.sample_thread_prop_val = None

    def long_wait(self):
        time.sleep(1)

    @property
    def sample_main_thread_property(self):
        return self.main_thread_prop_val

    @sample_main_thread_property.setter  # type: ignore
    @ensure_main_thread()
    def sample_main_thread_property(self, value):
        if QThread.currentThread() is not QCoreApplication.instance().thread():
            raise RuntimeError("Wrong thread")
        self.main_thread_prop_val = value
        self.assigment_done.emit()

    @property
    def sample_object_thread_property(self):
        return self.sample_thread_prop_val

    @sample_object_thread_property.setter  # type: ignore
    @ensure_object_thread()
    def sample_object_thread_property(self, value):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        self.sample_thread_prop_val = value
        self.assigment_done.emit()

    @ensure_main_thread
    def check_main_thread(self, a, *, b=1):
        if QThread.currentThread() is not QCoreApplication.instance().thread():
            raise RuntimeError("Wrong thread")
        self.main_thread_res = {"a": a, "b": b}
        self.assigment_done.emit()

    @ensure_object_thread
    def check_object_thread(self, a, *, b=1):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        self.object_thread_res = {"a": a, "b": b}
        self.assigment_done.emit()

    @ensure_object_thread(await_return=True)
    def check_object_thread_return(self, a):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        return a * 7

    @ensure_object_thread(await_return=True, timeout=200)
    def check_object_thread_return_timeout(self, a):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        time.sleep(1)
        return a * 7

    @ensure_object_thread(await_return=False)
    def check_object_thread_return_future(self, a: int):
        """sample docstring"""
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        time.sleep(0.4)
        return a * 7

    @ensure_main_thread(await_return=True)
    def check_main_thread_return(self, a):
        if QThread.currentThread() is not QCoreApplication.instance().thread():
            raise RuntimeError("Wrong thread")
        return a * 8


class LocalThread(QThread):
    def __init__(self, ob):
        super().__init__()
        self.ob = ob

    def run(self):
        assert QThread.currentThread() is not QCoreApplication.instance().thread()
        self.ob.check_main_thread(5, b=8)
        self.ob.main_thread_prop_val = "text2"


class LocalThread2(QThread):
    def __init__(self, ob):
        super().__init__()
        self.ob = ob
        self.executed = False

    def run(self):
        assert QThread.currentThread() is not QCoreApplication.instance().thread()
        assert self.ob.check_main_thread_return(5) == 40
        self.executed = True


def test_only_main_thread(qapp):
    ob = SampleObject()
    ob.check_main_thread(1, b=3)
    assert ob.main_thread_res == {"a": 1, "b": 3}
    ob.check_object_thread(2, b=4)
    assert ob.object_thread_res == {"a": 2, "b": 4}
    ob.sample_main_thread_property = 5
    assert ob.sample_main_thread_property == 5
    ob.sample_object_thread_property = 7
    assert ob.sample_object_thread_property == 7


def test_main_thread(qtbot):
    ob = SampleObject()
    t = LocalThread(ob)
    with qtbot.waitSignal(t.finished):
        t.start()

    assert ob.main_thread_res == {"a": 5, "b": 8}
    assert ob.sample_main_thread_property == "text2"


def test_main_thread_return(qtbot):
    ob = SampleObject()
    t = LocalThread2(ob)
    with qtbot.wait_signal(t.finished):
        t.start()
    assert t.executed


def test_names(qapp):
    ob = SampleObject()
    assert ob.check_object_thread.__name__ == "check_object_thread"
    assert ob.check_object_thread_return.__name__ == "check_object_thread_return"
    assert (
        ob.check_object_thread_return_timeout.__name__
        == "check_object_thread_return_timeout"
    )
    assert (
        ob.check_object_thread_return_future.__name__
        == "check_object_thread_return_future"
    )
    assert ob.check_object_thread_return_future.__doc__ == "sample docstring"
    signature = inspect.signature(ob.check_object_thread_return_future)
    assert len(signature.parameters) == 1
    assert next(iter(signature.parameters.values())).name == "a"
    assert next(iter(signature.parameters.values())).annotation is int
    assert ob.check_main_thread_return.__name__ == "check_main_thread_return"


@skip_on_ci
def test_object_thread_return(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    assert ob.check_object_thread_return(2) == 14
    assert ob.thread() is thread
    with qtbot.waitSignal(thread.finished):
        thread.quit()


@skip_on_ci
def test_object_thread_return_timeout(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    with pytest.raises(TimeoutError):
        ob.check_object_thread_return_timeout(2)
    with qtbot.waitSignal(thread.finished):
        thread.quit()


@skip_on_ci
def test_object_thread_return_future(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    future = ob.check_object_thread_return_future(2)
    assert isinstance(future, Future)
    assert future.result() == 14
    with qtbot.waitSignal(thread.finished):
        thread.quit()


@skip_on_ci
def test_object_thread(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    with qtbot.waitSignal(ob.assigment_done):
        ob.check_object_thread(2, b=4)
    assert ob.object_thread_res == {"a": 2, "b": 4}

    with qtbot.waitSignal(ob.assigment_done):
        ob.sample_object_thread_property = "text"

    assert ob.sample_object_thread_property == "text"
    assert ob.thread() is thread
    with qtbot.waitSignal(thread.finished):
        thread.quit()


@pytest.mark.parametrize("mode", ["method", "func", "wrapped"])
@pytest.mark.parametrize("deco", [ensure_main_thread, ensure_object_thread])
def test_ensure_thread_sig_inspection(deco, mode):
    class Emitter(QObject):
        sig = Signal(int, int, int)

    obj = Emitter()
    mock = Mock()

    if mode == "method":

        class Receiver(QObject):
            @deco
            def func(self, a: int, b: int):
                mock(a, b)

        r = Receiver()
        obj.sig.connect(r.func)
    elif deco == ensure_object_thread:
        return  # not compatible with function types

    elif mode == "wrapped":

        def wr(fun):
            @wraps(fun)
            def wr2(*args):
                mock(*args)
                return fun(*args) * 2

            return wr2

        @deco
        @wr
        def wrapped_func(a, b):
            return a + b

        obj.sig.connect(wrapped_func)

    elif mode == "func":

        @deco
        def func(a: int, b: int) -> None:
            mock(a, b)

        obj.sig.connect(func)

    # this is the crux of the test...
    # we emit 3 args, but the function only takes 2
    # this should normally work fine in Qt.
    # testing here that the decorator doesn't break it.
    obj.sig.emit(1, 2, 3)
    mock.assert_called_once_with(1, 2)


def test_main_thread_function(qtbot):
    """Testing decorator on a function rather than QObject method."""

    mock = Mock()

    class Emitter(QObject):
        sig = Signal(int, int, int)

    @ensure_main_thread
    def func(x: int) -> None:
        mock(x, QThread.currentThread())

    e = Emitter()
    e.sig.connect(func)

    with qtbot.waitSignal(e.sig):
        thread = threading.Thread(target=e.sig.emit, args=(1, 2, 3))
        thread.start()
        thread.join()

    mock.assert_called_once_with(1, QCoreApplication.instance().thread())
