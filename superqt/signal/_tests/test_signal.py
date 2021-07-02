import weakref
from types import FunctionType
from unittest.mock import MagicMock

import pytest

from superqt.signal import Receiver, Signal, SignalInstance


class Emitter:
    changed = Signal(int)


@pytest.fixture
def emitter():
    return Emitter()


@pytest.fixture
def receiver():
    class R(Receiver):
        expect_sender = None

        def assert_sender(self, *a):
            assert self.get_sender() is self.expect_sender

        def assert_not_sender(self, *a):
            # just to make sure we're actually calling it
            assert self.get_sender() is not self.expect_sender

    return R()


def test_basic_signal(emitter):
    """standard Qt usage, as class attribute"""
    mock = MagicMock()
    emitter.changed.connect(mock)
    emitter.changed.emit(1)
    mock.assert_called_once_with(1)


def test_basic_signal_blocked(emitter: Emitter):
    """standard Qt usage, as class attribute"""
    mock = MagicMock()
    emitter.changed.connect(mock)

    emitter.changed.emit(1)
    mock.assert_called_once_with(1)

    mock.reset_mock()
    with emitter.changed.blocked():
        emitter.changed.emit(1)
    mock.assert_not_called()


def test_disconnect(emitter: Emitter):
    mock = MagicMock()
    with pytest.raises(ValueError) as e:
        emitter.changed.disconnect(mock)
    assert "slot is not connected" in str(e)

    emitter.changed.connect(mock)
    emitter.changed.emit(1)
    mock.assert_called_once_with(1)

    mock.reset_mock()
    emitter.changed.disconnect(mock)
    emitter.changed.emit(1)
    mock.assert_not_called()


def test_slot_types(emitter: Emitter, receiver):
    assert len(emitter.changed._slots) == 0
    emitter.changed.connect(lambda x: print("hi"))
    assert len(emitter.changed._slots) == 1

    def f(x):
        pass

    emitter.changed.connect(f)
    assert len(emitter.changed._slots) == 2
    # connecting same function twice is (currently) OK
    emitter.changed.connect(f)
    assert len(emitter.changed._slots) == 3
    assert isinstance(emitter.changed._slots[-1], FunctionType)

    # bound methods
    emitter.changed.connect(receiver.assert_sender)
    assert len(emitter.changed._slots) == 4
    assert isinstance(emitter.changed._slots[-1], weakref.WeakKeyDictionary)

    class T:
        def x(self):
            pass

    emitter.changed.connect(T.x)
    assert len(emitter.changed._slots) == 5
    assert type(emitter.changed._slots[-1]) == FunctionType

    with pytest.raises(TypeError):
        emitter.changed.connect("not a callable")  # type: ignore


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


def test_signature_validation(emitter: Emitter):
    class Emitter:
        no_arg = Signal()
        one_arg = Signal(int)
        two_arg = Signal(int, int)

    def no_arg():
        ...

    def one_arg(a):
        ...

    def two_arg(a, b):
        ...

    def arg_kwarg(a, b=None):
        ...

    def any_arg(*a, **b):
        ...

    e = Emitter()

    e.no_arg.connect(no_arg)
    e.no_arg.connect(any_arg)
    with pytest.raises(TypeError) as err:
        e.no_arg.connect(one_arg)
    assert "Accepted: ()" in str(err)

    e.one_arg.connect(one_arg)
    e.one_arg.connect(arg_kwarg)
    e.one_arg.connect(any_arg)
    with pytest.raises(TypeError) as err:
        e.one_arg.connect(no_arg)
    assert "Accepted: (a0: int, /)" in str(err)
    with pytest.raises(TypeError):
        e.one_arg.connect(two_arg)

    e.two_arg.connect(two_arg)
    e.two_arg.connect(arg_kwarg)
    e.two_arg.connect(any_arg)
    with pytest.raises(TypeError) as err:
        e.two_arg.connect(one_arg)
    assert "Accepted: (a0: int, a1: int, /)" in str(err)
