# https://gist.github.com/FlorianRhiem/41a1ad9b694c14fb9ac3
from typing import Callable, List, Optional

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
    instances: List["CallCallable"] = []

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
    func: Optional[Callable] = None, await_return: bool = False, timeout: int = 1000
):
    """Decorator that ensures a function is called in the main QApplication thread.

    It can be applied to functions or methods.

    Parameters
    ----------
    func : callable
        The method to decorate, must be a method on a QObject.
    await_return : bool, optional
        Whether to block and wait for the result of the function, or return immediately.
        by default False
    timeout : int, optional
        If `await_return` is `True`, time (in milliseconds) to wait for the result
        before raising a TimeoutError, by default 1000
    """

    def _out_func(func):
        def _func(*args, **kwargs):
            return _run_in_thread(
                func,
                QCoreApplication.instance().thread(),
                await_return,
                timeout,
                *args,
                **kwargs
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def ensure_object_thread(
    func: Optional[Callable] = None, await_return: bool = False, timeout: int = 1000
):
    """Decorator that ensures a QObject method is called in the object's thread.

    It must be applied to methods of QObjects subclasses.

    Parameters
    ----------
    func : callable
        The method to decorate, must be a method on a QObject.
    await_return : bool, optional
        Whether to block and wait for the result of the function, or return immediately.
        by default False
    timeout : int, optional
        If `await_return` is `True`, time (in milliseconds) to wait for the result
        before raising a TimeoutError, by default 1000
    """

    def _out_func(func):
        def _func(self, *args, **kwargs):
            return _run_in_thread(
                func, self.thread(), await_return, timeout, self, *args, **kwargs
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def _run_in_thread(
    func: Callable, thread: QThread, await_return: bool, timeout: int, *args, **kwargs
):
    if thread is QThread.currentThread():
        if not await_return:
            func(*args, **kwargs)
            return
        return func(*args, **kwargs)
    f = CallCallable(func, *args, **kwargs)
    f.moveToThread(thread)
    if not await_return:
        QMetaObject.invokeMethod(f, "call", Qt.ConnectionType.QueuedConnection)
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
    QMetaObject.invokeMethod(f, "call", Qt.ConnectionType.QueuedConnection)
    loop.exec_()
    if len(res) == 0:
        raise TimeoutError("Not recived value")
    return res[0]
