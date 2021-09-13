import time
from concurrent.futures import Future, TimeoutError

import pytest

from superqt.qtcompat.QtCore import QCoreApplication, QObject, QThread, Signal
from superqt.utils import ensure_main_thread, ensure_object_thread


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
    def check_object_thread_return_future(self, a):
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
    thread.exit(0)


def test_main_thread(qtbot):
    ob = SampleObject()
    t = LocalThread(ob)
    with qtbot.waitSignal(t.finished):
        t.start()

    assert ob.main_thread_res == {"a": 5, "b": 8}
    assert ob.sample_main_thread_property == "text2"


def test_object_thread_return(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    assert ob.check_object_thread_return(2) == 14
    assert ob.thread() is thread
    thread.exit(0)


def test_object_thread_return_timeout(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    with pytest.raises(TimeoutError):
        ob.check_object_thread_return_timeout(2)
    thread.exit(0)


def test_object_thread_return_future(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    future = ob.check_object_thread_return_future(2)
    assert isinstance(future, Future)
    assert future.result() == 14
    thread.exit(0)


def test_main_thread_return(qtbot):
    ob = SampleObject()
    t = LocalThread2(ob)
    with qtbot.wait_signal(t.finished):
        t.start()
    assert t.executed
