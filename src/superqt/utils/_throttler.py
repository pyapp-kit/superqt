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
from enum import IntFlag, auto
from functools import partial
from typing import Any, Callable, Optional

from qtpy.QtCore import QObject, Qt, QTimer, Signal


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
        return self._kind

    def emissionPolicy(self) -> EmissionPolicy:
        return self._emissionPolicy

    def timeout(self) -> int:
        """Return current timeout in seconds."""
        return self._timer.interval()  # type: ignore

    def setTimeout(self, timeout: int) -> None:
        """Set timeout in seconds"""
        if self._timer.interval() != timeout:
            self._timer.setInterval(timeout)
            self.timeoutChanged.emit(timeout)

    def timerType(self) -> Qt.TimerType:
        return self._timer.timerType()

    def setTimerType(self, timerType: Qt.TimerType) -> None:
        """Set timer type"""
        if self._timer.timerType() != timerType:
            self._timer.setTimerType(timerType)
            self.timerTypeChanged.emit(timerType)

    def throttle(self) -> None:
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
        self._hasPendingEmission = False

    def flush(self) -> None:
        self._maybeEmitTriggered()

    def _emitTriggered(self) -> None:
        self._hasPendingEmission = False
        self.triggered.emit()

    def _maybeEmitTriggered(self) -> None:
        if self._hasPendingEmission:
            self._emitTriggered()

    Kind = Kind
    EmissionPolicy = EmissionPolicy


# ### Convenience classes ###


class QSignalThrottler(GenericSignalThrottler):
    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.Trailing,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(Kind.Throttler, policy, parent)


class QSignalDebouncer(GenericSignalThrottler):
    def __init__(
        self,
        policy: EmissionPolicy = EmissionPolicy.Trailing,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(Kind.Debouncer, policy, parent)


# below here part is unique to superqt (not from KD)


def qthrottled(
    func: Optional[Callable[..., None]] = None,
    timeout=100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
) -> Callable[..., None]:
    """Creates a throttled function that invokes func at most once per timeout.

    The throttled function comes with a cancel method to cancel delayed func
    invocations and a flush method to immediately invoke them. Provide options
    to indicate whether func should be invoked on the leading and/or trailing
    edge of the wait timeout. The func is invoked with the last arguments provided
    to the throttled function. Subsequent calls to the throttled function return
    the result of the last func invocation.
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Throttler)


def qdebounced(
    func: Optional[Callable[..., None]] = None,
    timeout=100,
    leading: bool = True,
    timer_type: Qt.TimerType = Qt.TimerType.PreciseTimer,
):
    """Creates a debounced function that delays invoking func at until `timeout`
    ms have elapsed since the last time the debounced function was invoked.

    The debounced function comes with a cancel method to cancel delayed func
    invocations and a flush method to immediately invoke them. Provide options to
    indicate whether func should be invoked on the leading and/or trailing edge
    of the wait timeout. The func is invoked with the last arguments provided to
    the debounced function. Subsequent calls to the debounced function return the
    result of the last func invocation.
    """
    return _make_decorator(func, timeout, leading, timer_type, Kind.Debouncer)


def _make_decorator(func, timeout, leading, timer_type, kind):
    def deco(func: Callable[..., None]) -> Callable[..., None]:
        policy = EmissionPolicy.Leading if leading else EmissionPolicy.Trailing
        throttle = GenericSignalThrottler(kind, policy)
        throttle.setTimerType(timer_type)
        throttle.setTimeout(timeout)
        last_f = None

        def inner(*args: Any, **kwargs: Any) -> None:
            nonlocal last_f
            if last_f is not None:
                throttle.triggered.disconnect(last_f)

            last_f = partial(func, *args, **kwargs) if args or kwargs else func
            throttle.triggered.connect(last_f)
            throttle.throttle()

        inner.cancel = throttle.cancel
        inner.flush = throttle.flush
        inner.set_timeout = throttle.setTimeout
        return inner

    return deco(func) if func is not None else deco
