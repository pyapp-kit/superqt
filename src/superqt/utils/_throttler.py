"""Adapted for python from the KDToolBox

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
import sys
from concurrent.futures import Future
from enum import IntFlag, auto
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generic, Optional, TypeVar, Union, overload

from qtpy.QtCore import QObject, Qt, QTimer, Signal
from typing_extensions import Literal, ParamSpec

if TYPE_CHECKING:
    from qtpy.QtCore import SignalInstance


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
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._kind = kind
        self._emissionPolicy = emissionPolicy
        self._hasPendingEmission = False

        self._timer = QTimer()
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
        return self._timer.interval()  # type: ignore

    def setTimeout(self, timeout: int) -> None:
        """Set timeout in milliseconds"""
        if self._timer.interval() != timeout:
            self._timer.setInterval(timeout)
            self.timeoutChanged.emit(timeout)

    def timerType(self) -> Qt.TimerType:
        """Return current Qt.TimerType."""
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

        assert self._timer.isActive()

    def cancel(self) -> None:
        """ "Cancel and pending emissions."""
        self._hasPendingEmission = False

    def flush(self) -> None:
        """ "Force emission of any pending emissions."""
        self._maybeEmitTriggered()

    def _emitTriggered(self) -> None:
        self._hasPendingEmission = False
        self.triggered.emit()
        self._timer.start()

    def _maybeEmitTriggered(self) -> None:
        if self._hasPendingEmission:
            self._emitTriggered()

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
        parent: Optional[QObject] = None,
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
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(Kind.Debouncer, policy, parent)


# below here part is unique to superqt (not from KD)

P = ParamSpec("P")
R = TypeVar("R")

if TYPE_CHECKING:
    from typing_extensions import Protocol

    class ThrottledCallable(Generic[P, R], Protocol):
        triggered: "SignalInstance"

        def cancel(self) -> None:
            ...

        def flush(self) -> None:
            ...

        def set_timeout(self, timeout: int) -> None:
            ...

        if sys.version_info < (3, 9):

            def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Future:
                ...

        else:

            def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Future[R]:
                ...


@overload
def qthrottled(
    func: Callable[P, R],
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> "ThrottledCallable[P, R]":
    ...


@overload
def qthrottled(
    func: Literal[None] = None,
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> Callable[[Callable[P, R]], "ThrottledCallable[P, R]"]:
    ...


def qthrottled(
    func: Optional[Callable[P, R]] = None,
    timeout: int = 100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> Union[
    "ThrottledCallable[P, R]", Callable[[Callable[P, R]], "ThrottledCallable[P, R]"]
]:
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
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Throttler)


@overload
def qdebounced(
    func: Callable[P, R],
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> "ThrottledCallable[P, R]":
    ...


@overload
def qdebounced(
    func: Literal[None] = None,
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> Callable[[Callable[P, R]], "ThrottledCallable[P, R]"]:
    ...


def qdebounced(
    func: Optional[Callable[P, R]] = None,
    timeout: int = 100,
    leading: bool = False,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> Union[
    "ThrottledCallable[P, R]", Callable[[Callable[P, R]], "ThrottledCallable[P, R]"]
]:
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
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Debouncer)


def _make_decorator(
    func: Optional[Callable[P, R]],
    timeout: int,
    leading: bool,
    timer_type: Qt.TimerType,
    kind: Kind,
) -> Union[
    "ThrottledCallable[P, R]", Callable[[Callable[P, R]], "ThrottledCallable[P, R]"]
]:
    def deco(func: Callable[P, R]) -> "ThrottledCallable[P, R]":
        policy = EmissionPolicy.Leading if leading else EmissionPolicy.Trailing
        throttle = GenericSignalThrottler(kind, policy)
        throttle.setTimerType(timer_type)
        throttle.setTimeout(timeout)
        last_f = None
        future: Optional[Future] = None

        @wraps(func)
        def inner(*args: P.args, **kwargs: P.kwargs) -> Future:
            nonlocal last_f
            nonlocal future
            if last_f is not None:
                throttle.triggered.disconnect(last_f)
            if future is not None and not future.done():
                future.cancel()

            future = Future()
            last_f = lambda: future.set_result(func(*args, **kwargs))  # noqa
            throttle.triggered.connect(last_f)
            throttle.throttle()
            return future

        setattr(inner, "cancel", throttle.cancel)
        setattr(inner, "flush", throttle.flush)
        setattr(inner, "set_timeout", throttle.setTimeout)
        setattr(inner, "triggered", throttle.triggered)
        return inner  # type: ignore

    return deco(func) if func is not None else deco
