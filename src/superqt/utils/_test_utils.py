from contextlib import contextmanager

from superqt.utils._throttler import GenericSignalThrottler


def _throttle_mock(self):
    self.triggered.emit()


def _flush_mock(self):
    """There are no waiting events."""


@contextmanager
def disable_throttling():
    """Context manager for disabling throttling during tests."""
    prev = GenericSignalThrottler.throttle
    prev_flush = GenericSignalThrottler.flush
    GenericSignalThrottler.throttle = _throttle_mock
    GenericSignalThrottler.flush = _flush_mock
    try:
        yield
    finally:
        GenericSignalThrottler.throttle = prev
        GenericSignalThrottler.flush = prev_flush
