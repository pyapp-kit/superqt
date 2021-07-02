import weakref
from types import FunctionType
from unittest.mock import MagicMock

import pytest

from superqt.signal import Receiver, Signal, SignalInstance
from superqt.signal._signal import (
    _arg_count_compatible,
    _arg_types_compatible,
    sigs_compatible,
)


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

    # a slot may have a shorter signature than the signal it receives
    # because it can ignore extra arguments.

    class Emitter:
        no_arg = Signal()
        one_arg = Signal(int)
        two_arg = Signal(int, int)

    # fmt: off
    def no_arg(): ...
    def one_arg(a): ...
    def two_arg(a, b): ...
    def arg_kwarg(a, b=None): ...
    def any_arg(*a, **b): ...
    # fmt: on

    e = Emitter()

    e.no_arg.connect(no_arg)
    e.no_arg.connect(any_arg)
    with pytest.raises(TypeError) as err:
        e.no_arg.connect(one_arg)
    assert "Accepted: ()" in str(err)

    e.one_arg.connect(one_arg)
    e.one_arg.connect(arg_kwarg)
    e.one_arg.connect(any_arg)
    e.one_arg.connect(no_arg)
    with pytest.raises(TypeError):
        e.one_arg.connect(two_arg)

    e.two_arg.connect(two_arg)
    e.two_arg.connect(arg_kwarg)
    e.two_arg.connect(any_arg)
    e.two_arg.connect(one_arg)


def test_arg_count_compatible():
    sig = Signal._build_signature(str, str)  # what this signal will emit

    # a slot may have a shorter signature than the signal it receives
    # because it can ignore extra arguments.
    assert _arg_count_compatible(lambda x, y: None, sig)
    assert _arg_count_compatible(lambda x, y, z=None: None, sig)
    assert _arg_count_compatible(lambda x: None, sig)
    assert _arg_count_compatible(lambda *x: None, sig)
    assert _arg_count_compatible(lambda *x, z=None: None, sig)
    assert _arg_count_compatible(lambda: None, sig)
    # but not more
    assert not _arg_count_compatible(lambda x, y, z: None, sig)
    # unless they are optional or have defaults
    assert _arg_count_compatible(lambda x, y, *z: None, sig)
    assert _arg_count_compatible(lambda x, y, z=None: None, sig)

    assert _arg_count_compatible(MagicMock(), sig)


def test_arg_type_compatible():
    sig = Signal._build_signature(str, int)  # what this signal will emit

    # fmt: off
    def f_str_int(a: str, b: int): ...
    def f_str_none(a: str, b): ...  # missing annotations are ok
    def f_str_str(a: str, b: str): ...  # b is wrong
    def f_str(a: str): ...  # fails if strict_length is True
    def f_int_int(a: int, b: int): ...
    def f(): ...  # fails if strict_length is True
    # fmt: on

    assert _arg_types_compatible(f_str_int, sig)
    assert _arg_types_compatible(f_str_none, sig)
    assert not _arg_types_compatible(f_str_str, sig)
    assert not _arg_types_compatible(f_int_int, sig)
    assert not _arg_types_compatible(f_str, sig, strict_length=True)
    assert _arg_types_compatible(f_str, sig)
    assert not _arg_types_compatible(f, sig, strict_length=True)
    assert _arg_types_compatible(f, sig)

    assert _arg_types_compatible(MagicMock(), sig)


def test_sigs_compatible():
    """Test that"""
    sig = Signal._build_signature(str, int)  # what this signal will emit

    # a slot may have a shorter signature than the signal it receives
    # because it can ignore extra arguments.

    # fmt: off
    def f_str_int(a: str, b: int, *c): ...
    def f_str_str(a: str, b: str): ...  # b is wrong
    def f_str_int_none(a: str, b: int, c): ...  # too many
    def f_str_none(a: str, b): ...  # missing annotations ok
    def f_str(a: str): ...  # less ok
    def f_int(a: int): ...  # but not if wrong annotation
    def f(): ...
    # fmt: on

    assert sigs_compatible(f_str_int, sig)
    assert not sigs_compatible(f_str_str, sig)
    assert sigs_compatible(f_str_str, sig, check_types=False)
    assert not sigs_compatible(f_str_int_none, sig)
    assert sigs_compatible(f_str_none, sig)
    assert sigs_compatible(f_str, sig)
    assert not sigs_compatible(f_int, sig)
    assert sigs_compatible(f, sig)

    from inspect import Signature

    assert _arg_count_compatible(MagicMock(), Signature())
