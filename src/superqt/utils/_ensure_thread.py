# https://gist.github.com/FlorianRhiem/41a1ad9b694c14fb9ac3
from __future__ import annotations

import inspect
from concurrent.futures import Future
from functools import wraps
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, ClassVar, overload

from qtpy.QtCore import (
    QCoreApplication,
    QMetaObject,
    QObject,
    Qt,
    QThread,
    Signal,
    Slot,
)

if TYPE_CHECKING:
    from typing import TypeVar

    from typing_extensions import Literal, ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")


class CallCallable(QObject):
    finished = Signal(object)
    instances: ClassVar[list[CallCallable]] = []

    def __init__(_call_callable_self_, callable, *args, **kwargs):
        super().__init__()
        _call_callable_self_._callable = callable
        _call_callable_self_._args = args
        _call_callable_self_._kwargs = kwargs
        CallCallable.instances.append(_call_callable_self_)

    @Slot()
    def call(self):
        CallCallable.instances.remove(self)
        res = self._callable(*self._args, **self._kwargs)
        self.finished.emit(res)


# fmt: off
@overload
def ensure_main_thread(
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
@overload
def ensure_main_thread(
    func: Callable[P, R],
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[P, R]: ...
@overload
def ensure_main_thread(
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, Future[R]]]: ...
@overload
def ensure_main_thread(
    func: Callable[P, R],
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[P, Future[R]]: ...
# fmt: on


def ensure_main_thread(
    func: Callable | None = None, await_return: bool = False, timeout: int = 1000
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
        src = f"""
        def {func_.__name__}{inspect.signature(func_)}:
            return _run_in_thread(
                func_,
                QCoreApplication.instance().thread(),
                await_return,
                timeout,
                **locals(),
            )
        """
        localns: dict[str, Any] = {}
        exec(  # noqa S102
            compile(dedent(src), "<string>", "exec"),
            {
                "func_": func_,
                "_run_in_thread": _run_in_thread,
                "QCoreApplication": QCoreApplication,
                "await_return": await_return,
                "timeout": timeout,
            },
            localns,
        )
        return wraps(func_)(localns[func_.__name__])

    return _out_func if func is None else _out_func(func)


# fmt: off
@overload
def ensure_object_thread(
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
@overload
def ensure_object_thread(
    func: Callable[P, R],
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[P, R]: ...
@overload
def ensure_object_thread(
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, Future[R]]]: ...
@overload
def ensure_object_thread(
    func: Callable[P, R],
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[P, Future[R]]: ...
# fmt: on


def ensure_object_thread(
    func: Callable | None = None, await_return: bool = False, timeout: int = 1000
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
        sig = inspect.signature(func_)
        first_arg = next(iter(sig.parameters))

        src = f"""
        def {func_.__name__}{sig}:
            kwargs = locals()
            self = kwargs.pop("{first_arg}")
            return _run_in_thread(
                func_,
                self.thread(),
                await_return,
                timeout,
                self,
                **kwargs,
            )
        """
        localns: dict[str, Any] = {}
        exec(  # noqa S102
            compile(dedent(src), "<string>", "exec"),
            {
                "func_": func_,
                "_run_in_thread": _run_in_thread,
                "QCoreApplication": QCoreApplication,
                "await_return": await_return,
                "timeout": timeout,
            },
            localns,
        )
        return wraps(func_)(localns[func_.__name__])

    return _out_func if func is None else _out_func(func)


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
    QMetaObject.invokeMethod(f, "call", Qt.ConnectionType.QueuedConnection)  # type: ignore  # noqa
    return future.result(timeout=timeout / 1000) if await_return else future
