import pytest

from superqt.utils._throttler import GenericSignalThrottler


def _throttle_mock(self):
    self.triggered.emit()


def _flush_mock(self):
    """There are no waiting events."""


@pytest.fixture()
def disable_throttling(monkeypatch):
    monkeypatch.setattr(GenericSignalThrottler, "throttle", _throttle_mock)
    monkeypatch.setattr(GenericSignalThrottler, "flush", _flush_mock)
