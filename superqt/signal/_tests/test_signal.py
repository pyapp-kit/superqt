from unittest.mock import MagicMock

import pytest

from superqt.signal import Receiver, Signal, SignalInstance


@pytest.fixture
def emitter():
    class Emitter:
        changed = Signal(int)

    return Emitter()


@pytest.fixture
def receiver():
    class R(Receiver):
        expect_sender = None

        def assert_sender(self):
            assert self.get_sender() is self.expect_sender

        def assert_not_sender(self):
            # just to make sure we're actually calling it
            assert self.get_sender() is not self.expect_sender

    return R()


def test_basic_signal(emitter):
    """standard Qt usage, as class attribute"""
    mock = MagicMock()
    emitter.changed.connect(mock)
    emitter.changed.emit(1)
    mock.assert_called_once_with(1)


def test_basic_signal_blocked(emitter):
    """standard Qt usage, as class attribute"""
    mock = MagicMock()
    emitter.changed.connect(mock)
    emitter.changed.emit(1)
    mock.assert_called_once_with(1)


def test_basic_signal_with_sender(emitter, receiver):
    """standard Qt usage, as class attribute"""
    receiver.expect_sender = emitter

    assert receiver.get_sender() is None
    emitter.changed.connect(receiver.assert_sender)
    emitter.changed.emit()

    # back to none after the call is over.
    assert receiver.get_sender() is None
    emitter.changed.disconnect()

    # sanity check... to make sure that methods are in fact being called.
    emitter.changed.connect(receiver.assert_not_sender)
    with pytest.raises(AssertionError):
        emitter.changed.emit()


def test_signal_instance():
    """make a signal instance without a class"""
    signal = SignalInstance()
    mock = MagicMock()
    signal.connect(mock)
    signal.emit(1)
    mock.assert_called_once_with(1)


def test_signal_instance_error():
    """without a class"""
    signal = Signal()
    mock = MagicMock()
    with pytest.raises(AttributeError) as e:
        signal.connect(mock)
    assert "Signal() class attribute" in str(e)
