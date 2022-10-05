# https://gist.github.com/FlorianRhiem/41a1ad9b694c14fb9ac3
from concurrent.futures import Future
from functools import wraps
from typing import Callable, List, Optional

from qtpy.QtCore import (
    QCoreApplication,
    QMetaObject,
    QObject,
    Qt,
    QThread,
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

    def _out_func(func_):
        @wraps(func_)
        def _func(*args, **kwargs):
            return _run_in_thread(
                func_,
                QCoreApplication.instance().thread(),
                await_return,
                timeout,
                *args,
                **kwargs,
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

    def _out_func(func_):
        @wraps(func_)
        def _func(self, *args, **kwargs):
            return _run_in_thread(
                func_, self.thread(), await_return, timeout, self, *args, **kwargs
            )

        return _func

    if func is None:
        return _out_func
    return _out_func(func)


def _run_in_thread(
    func: Callable,
    thread: QThread,
    await_return: bool,
    timeout: int,
    *args,
    **kwargs,
):
    future = Future()  # type: ignore
    if thread is QThread.currentThread():
        result = func(*args, **kwargs)
        if not await_return:
            future.set_result(result)
            return future
        return result
    f = CallCallable(func, *args, **kwargs)
    f.moveToThread(thread)
    f.finished.connect(future.set_result, Qt.ConnectionType.DirectConnection)
    QMetaObject.invokeMethod(f, "call", Qt.ConnectionType.QueuedConnection)  # type: ignore
    return future.result(timeout=timeout / 1000) if await_return else future
