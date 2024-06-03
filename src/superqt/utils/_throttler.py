"""Adapted for python from the KDToolBox.

https://github.com/KDAB/KDToolBox/tree/master/qt/KDSignalThrottler

MIT License

Copyright (C) 2019-2022 Klarälvdalens Datakonsult AB, a KDAB Group company,
info@kdab.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from __future__ import annotations

import warnings
from concurrent.futures import Future
from contextlib import suppress
from enum import IntFlag, auto
from functools import wraps
from inspect import signature
from types import MethodType
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, overload
from weakref import WeakKeyDictionary, WeakMethod

from qtpy.QtCore import QObject, Qt, QTimer, Signal

from ._util import get_max_args

if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    P = ParamSpec("P")
# maintain runtime compatibility with older typing_extensions
else:
    try:
        from typing_extensions import ParamSpec

        P = ParamSpec("P")
    except ImportError:
        P = TypeVar("P")

R = TypeVar("R")
REF_ERROR = (
    "To use qthrottled or qdebounced as a method decorator, "
    "objects must have  `__dict__` or be weak referenceable. "
    "Please either add `__weakref__` to `__slots__` or use"
    "qthrottled/qdebounced as a function (not a decorator)."
)


class Kind(IntFlag):
    Throttler = auto()
    Debouncer = auto()


class EmissionPolicy(IntFlag):
    Trailing = auto()
    Leading = auto()


class GenericSignalThrottler(QObject):
    triggered = Signal()
    timeoutChanged = Signal(int)
    timerTypeChanged = Signal(Qt.TimerType)

    def __init__(
        self,
        kind: Kind,
        emissionPolicy: EmissionPolicy,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)

        self._kind = kind
        self._emissionPolicy = emissionPolicy
        self._hasPendingEmission = False

        self._timer = QTimer(parent=self)
        self._timer.setSingleShot(True)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._maybeEmitTriggered)

    def kind(self) -> Kind:
        """Return the kind of throttler (throttler or debouncer)."""
        return self._kind

    def emissionPolicy(self) -> EmissionPolicy:
        """Return the emission policy (trailing or leading)."""
        return self._emissionPolicy

    def timeout(self) -> int:
        """Return current timeout in milliseconds."""
        return self._timer.interval()

    def setTimeout(self, timeout: int) -> None:
        """Set timeout in milliseconds."""
        if self._timer.interval() != timeout:
            self._timer.setInterval(timeout)
            self.timeoutChanged.emit(timeout)

    def timerType(self) -> Qt.TimerType:
        """Return current `Qt.TimerType`."""
        return self._timer.timerType()

    def setTimerType(self, timerType: Qt.TimerType) -> None:
        """Set current Qt.TimerType."""
        if self._timer.timerType() != timerType:
            self._timer.setTimerType(timerType)
            self.timerTypeChanged.emit(timerType)

    def throttle(self) -> None:
        """Emit triggered if not running, then start timer."""
        # public slot
        self._hasPendingEmission = True
        # Emit only if we haven't emitted already. We know if that's
        # the case by checking if the timer is running.
        if (
            self._emissionPolicy is EmissionPolicy.Leading
            and not self._timer.isActive()
        ):
            self._emitTriggered()

        # The timer is started in all cases. If we got a signal, and we're Leading,
        # and we did emit because of that, then we don't re-emit when the timer fires
        # (unless we get ANOTHER signal).
        if self._kind is Kind.Throttler:  # sourcery skip: merge-duplicate-blocks
            if not self._timer.isActive():
                self._timer.start()  # actual start, not restart
        elif self._kind is Kind.Debouncer:
            self._timer.start()  # restart

    def cancel(self) -> None:
        """Cancel any pending emissions."""
        self._hasPendingEmission = False

    def flush(self, restart_timer: bool = True) -> None:
        """
        Force emission of any pending emissions.

        Parameters
        ----------
        restart_timer : bool
            Whether to restart the timer after flushing.
            Defaults to True.
        """
        self._maybeEmitTriggered(restart_timer=restart_timer)

    def _emitTriggered(self) -> None:
        self._hasPendingEmission = False
        self.triggered.emit()
        self._timer.start()

    def _maybeEmitTriggered(self, restart_timer: bool = True) -> None:
        if self._hasPendingEmission:
            self._emitTriggered()
        if not restart_timer:
            self._timer.stop()

    Kind = Kind
    EmissionPolicy = EmissionPolicy


# ### Convenience classes ###


class QSignalThrottler(GenericSignalThrottler):
    """A Signal Throttler.

    This object's `triggered` signal will emit at most once per timeout
    (set with setTimeout()).
    """

    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.Leading,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(Kind.Throttler, policy, parent)


class QSignalDebouncer(GenericSignalThrottler):
    """A Signal Debouncer.

    This object's `triggered` signal will not be emitted until `self.timeout()`
    milliseconds have elapsed since the last time `triggered` was emitted.
    """

    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.Trailing,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(Kind.Debouncer, policy, parent)


# below here part is unique to superqt (not from KD)


def _weak_func(func: Callable[P, R]) -> Callable[P, R]:
    if isinstance(func, MethodType):
        # this is a bound method, we need to avoid strong references
        try:
            weak_method = WeakMethod(func)
        except TypeError as e:
            raise TypeError(REF_ERROR) from e

        def weak_func(*args, **kwargs):
            if method := weak_method():
                return method(*args, **kwargs)
            warnings.warn(
                "Method has been garbage collected", RuntimeWarning, stacklevel=2
            )

        return weak_func

    return func


class ThrottledCallable(GenericSignalThrottler, Generic[P, R]):
    def __init__(
        self,
        func: Callable[P, R],
        kind: Kind,
        emissionPolicy: EmissionPolicy,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(kind, emissionPolicy, parent)

        self._future: Future[R] = Future()

        self._is_static_method: bool = False
        if isinstance(func, staticmethod):
            self._is_static_method = True
            func = func.__func__

        max_args = get_max_args(func)
        with suppress(TypeError, ValueError):
            self.__signature__ = signature(func)

        self._func = _weak_func(func)
        self.__wrapped__ = self._func

        self._args: tuple = ()
        self._kwargs: dict = {}
        self.triggered.connect(self._set_future_result)
        self._name = None

        self._obj_dkt: WeakKeyDictionary[Any, ThrottledCallable] = WeakKeyDictionary()

        # even if we were to compile __call__ with a signature matching that of func,
        # PySide wouldn't correctly inspect the signature of the ThrottledCallable
        # instance: https://bugreports.qt.io/browse/PYSIDE-2423
        # so we do it ourselfs and limit the number of positional arguments
        # that we pass to func
        self._max_args: int | None = max_args

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> "Future[R]":  # noqa
        if not self._future.done():
            self._future.cancel()

        self._future = Future()
        self._args = args
        self._kwargs = kwargs

        self.throttle()
        return self._future

    def _set_future_result(self):
        result = self._func(*self._args[: self._max_args], **self._kwargs)
        self._future.set_result(result)

    def __set_name__(self, owner, name):
        if not self._is_static_method:
            self._name = name

    def _get_throttler(self, instance, owner, parent, obj, name):
        try:
            bound_method = self._func.__get__(instance, owner)
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                f"Failed to bind function {self._func!r} to object {instance!r}"
            ) from e
        throttler = ThrottledCallable(
            bound_method,
            self._kind,
            self._emissionPolicy,
            parent=parent,
        )
        throttler.setTimerType(self.timerType())
        throttler.setTimeout(self.timeout())
        try:
            setattr(obj, name, throttler)
        except AttributeError:
            try:
                self._obj_dkt[obj] = throttler
            except TypeError as e:
                raise TypeError(REF_ERROR) from e
        return throttler

    def __get__(self, instance, owner):
        if instance is None or not self._name:
            return self

        if instance in self._obj_dkt:
            return self._obj_dkt[instance]

        parent = self.parent()
        if parent is None and isinstance(instance, QObject):
            parent = instance

        return self._get_throttler(instance, owner, parent, instance, self._name)


@overload
def qthrottled(
    func: Callable[P, R],
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> ThrottledCallable[P, R]: ...


@overload
def qthrottled(
    func: None = ...,
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> Callable[[Callable[P, R]], ThrottledCallable[P, R]]: ...


def qthrottled(
    func: Callable[P, R] | None = None,
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> ThrottledCallable[P, R] | Callable[[Callable[P, R]], ThrottledCallable[P, R]]:
    """Creates a throttled function that invokes func at most once per timeout.

    The throttled function comes with a `cancel` method to cancel delayed func
    invocations and a `flush` method to immediately invoke them. Options
    to indicate whether func should be invoked on the leading and/or trailing
    edge of the wait timeout. The func is invoked with the last arguments provided
    to the throttled function. Subsequent calls to the throttled function return
    the result of the last func invocation.

    This decorator may be used with or without parameters.

    Parameters
    ----------
    func : Callable
        A function to throttle
    timeout : int
        Timeout in milliseconds to wait before allowing another call, by default 100
    leading : bool
        Whether to invoke the function on the leading edge of the wait timer,
        by default True
    timer_type : Qt.TimerType
        The timer type. by default `Qt.TimerType.PreciseTimer`
        One of:
            - `Qt.PreciseTimer`: Precise timers try to keep millisecond accuracy
            - `Qt.CoarseTimer`: Coarse timers try to keep accuracy within 5% of the
              desired interval
            - `Qt.VeryCoarseTimer`: Very coarse timers only keep full second accuracy
    parent: QObject or None
        Parent object for timer. If using qthrottled as function it may be usefull
        for cleaning data
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Throttler, parent)


@overload
def qdebounced(
    func: Callable[P, R],
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> ThrottledCallable[P, R]: ...


@overload
def qdebounced(
    func: None = ...,
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> Callable[[Callable[P, R]], ThrottledCallable[P, R]]: ...


def qdebounced(
    func: Callable[P, R] | None = None,
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
    parent: QObject | None = None,
) -> ThrottledCallable[P, R] | Callable[[Callable[P, R]], ThrottledCallable[P, R]]:
    """Creates a debounced function that delays invoking `func`.

    `func` will not be invoked until `timeout` ms have elapsed since the last time
    the debounced function was invoked.

    The debounced function comes with a `cancel` method to cancel delayed func
    invocations and a `flush` method to immediately invoke them. Options
    indicate whether func should be invoked on the leading and/or trailing edge
    of the wait timeout. The func is invoked with the *last* arguments provided to
    the debounced function. Subsequent calls to the debounced function return the
    result of the last `func` invocation.

    This decorator may be used with or without parameters.

    Parameters
    ----------
    func : Callable
        A function to throttle
    timeout : int
        Timeout in milliseconds to wait before allowing another call, by default 100
    leading : bool
        Whether to invoke the function on the leading edge of the wait timer,
        by default False
    timer_type : Qt.TimerType
        The timer type. by default `Qt.TimerType.PreciseTimer`
        One of:
            - `Qt.PreciseTimer`: Precise timers try to keep millisecond accuracy
            - `Qt.CoarseTimer`: Coarse timers try to keep accuracy within 5% of the
              desired interval
            - `Qt.VeryCoarseTimer`: Very coarse timers only keep full second accuracy
    parent: QObject or None
        Parent object for timer. If using qthrottled as function it may be usefull
        for cleaning data
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Debouncer, parent)


def _make_decorator(
    func: Callable[P, R] | None,
    timeout: int,
    leading: bool,
    timer_type: Qt.TimerType,
    kind: Kind,
    parent: QObject | None = None,
) -> ThrottledCallable[P, R] | Callable[[Callable[P, R]], ThrottledCallable[P, R]]:
    def deco(func: Callable[P, R]) -> ThrottledCallable[P, R]:
        nonlocal parent

        instance: object | None = getattr(func, "__self__", None)
        if isinstance(instance, QObject) and parent is None:
            parent = instance
        policy = EmissionPolicy.Leading if leading else EmissionPolicy.Trailing
        obj = ThrottledCallable(func, kind, policy, parent=parent)
        obj.setTimerType(timer_type)
        obj.setTimeout(timeout)

        if instance is not None:
            # this is a bound method, we need to avoid strong references,
            # and functools.wraps will prevent garbage collection on bound methods
            return obj
        return wraps(func)(obj)

    return deco(func) if func is not None else deco
