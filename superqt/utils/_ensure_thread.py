# https://gist.github.com/FlorianRhiem/41a1ad9b694c14fb9ac3
from typing import Callable, Optional

from superqt.qtcompat.QtCore import (
    QCoreApplication,
    QEventLoop,
    QMetaObject,
    QObject,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)


class CallCallable(QObject):
    finished = Signal(object)
    instances = []

    def __init__(self, callable, *args, **kwargs):
        super().__init__()
        self._callable = callable
        self._args = args
        self._kwargs = kwargs
        CallCallable.instances.append(self)

    @Slot()
    def call(self):
        CallCallable.instances.remove(self)
        res = self._callable(*self._args, **self._kwargs)
        self.finished.emit(res)


def ensure_main_thread(
    func: Optional[Callable] = None, no_return: bool = True, timeout: int = 1000
):
    """
    This is decorator which move function call to main thread (Thread in which QApplication was created).
    It could be applied to functions and methods.

    :param bool no_return: if wait on result of function result, default True
    :param int timeout: timeout for waiting on result
    """

    def _out_func(func):
        def _func(*args, **kwargs):
            return _run_in_thread(
                func,
                QCoreApplication.instance().thread(),
                no_return,
                timeout,
                *args,
                **kwargs
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def ensure_object_thread(
    func: Optional[Callable] = None, no_return: bool = True, timeout: int = 1000
):
    """
    This is decorator which move function call to object thread.
    It could be applied to methods of QObject instances.

    :param bool no_return: if wait on result of function result, default True
    :param int timeout: timeout for waiting on result
    """

    def _out_func(func):
        def _func(self, *args, **kwargs):
            return _run_in_thread(
                func, self.thread(), no_return, timeout, self, *args, **kwargs
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def _run_in_thread(
    func: Callable, thread: QThread, no_return: bool, timeout: int, *args, **kwargs
):
    if thread is QThread.currentThread():
        if no_return:
            func(*args, **kwargs)
            return
        return func(*args, **kwargs)
    f = CallCallable(func, *args, **kwargs)
    f.moveToThread(thread)
    if no_return:
        QMetaObject.invokeMethod(f, "call", Qt.QueuedConnection)
        return

    res = []

    def set_res(data):
        res.append(data)

    f.finished.connect(set_res)
    timer = QTimer()
    timer.setSingleShot(True)
    loop = QEventLoop()
    f.finished.connect(loop.quit)
    timer.timeout.connect(loop.quit)
    timer.start(timeout)
    QMetaObject.invokeMethod(f, "call", Qt.QueuedConnection)
    loop.exec_()
    if len(res) == 0:
        raise TimeoutError("Not recived value")
    return res[0]
