import time

from superqt.qtcompat.QtCore import QCoreApplication, QObject, QThread, Signal
from superqt.utils import ensure_main_thread, ensure_object_thread


class SampleObject(QObject):
    assigment_done = Signal()

    def __init__(self):
        super().__init__()
        self.main_thread_res = {}
        self.object_thread_res = {}

    def long_wait(self):
        time.sleep(1)

    @ensure_main_thread()
    def check_main_thread(self, a, *, b=1):
        if QThread.currentThread() is not QCoreApplication.instance().thread():
            raise RuntimeError("Wrong thread")
        self.main_thread_res = {"a": a, "b": b}
        self.assigment_done.emit()

    @ensure_object_thread()
    def check_object_thread(self, a, *, b=1):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        self.object_thread_res = {"a": a, "b": b}
        self.assigment_done.emit()

    @ensure_object_thread(no_return=False)
    def check_object_thread_return(self, a):
        if QThread.currentThread() is not self.thread():
            raise RuntimeError("Wrong thread")
        return a * 7

    @ensure_main_thread(no_return=False)
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


def test_object_thread(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    with qtbot.waitSignal(ob.assigment_done):
        ob.check_object_thread(2, b=4)
    assert ob.thread() is thread
    thread.exit(0)
    assert ob.object_thread_res == {"a": 2, "b": 4}


def test_main_thread(qtbot):
    ob = SampleObject()
    t = LocalThread(ob)
    with qtbot.waitSignal(ob.assigment_done, timeout=10000000):
        t.start()

    assert ob.main_thread_res == {"a": 5, "b": 8}


def test_object_thread_return(qtbot):
    ob = SampleObject()
    thread = QThread()
    thread.start()
    ob.moveToThread(thread)
    assert ob.check_object_thread_return(2) == 14
    assert ob.thread() is thread
    thread.exit(0)


def test_main_thread_return(qtbot):
    ob = SampleObject()
    t = LocalThread2(ob)
    with qtbot.wait_signal(t.finished):
        t.start()
    assert t.executed
