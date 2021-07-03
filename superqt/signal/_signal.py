from __future__ import annotations

import weakref
from contextlib import contextmanager
from functools import wraps
from inspect import Parameter, Signature, ismethod, signature
from typing import TYPE_CHECKING, Any, Callable, Union, overload

if TYPE_CHECKING:
    CallbackType = Callable[..., None]
    SlotRef = Union[CallbackType, weakref.WeakKeyDictionary[object, CallbackType]]


class Signal:

    # valid callback signatures for this signal.
    if TYPE_CHECKING:
        signatures: tuple[Signature, ...]
        _signal_instances: dict[Signal, weakref.WeakKeyDictionary[Any, SignalInstance]]

    def __init__(self, *types: Any) -> None:
        self._signal_instances = {}

        if not types:
            # single signature, no parameters
            self.signatures = (Signature(),)
        elif not isinstance(types[0], (list, tuple, Signature)):
            # single signature, with parameters
            self.signatures = (Signal._build_signature(*types),)
        else:
            # multiple signatures
            _signatures: list[Signature] = []
            for t in types:
                if isinstance(t, Signature):
                    _signatures.append(t)
                elif isinstance(t, (list, tuple)):
                    _signatures.append(Signal._build_signature(*t))
                else:
                    raise TypeError(
                        "each signature in a multi-signature sequence must be "
                        "experessed as a Signature, list, or tuple"
                    )
            self.signatures = tuple(_signatures)

    @staticmethod
    def _build_signature(*types: type) -> Signature:
        params = [
            Parameter(name=f"a{i}", kind=Parameter.POSITIONAL_ONLY, annotation=t)
            for i, t in enumerate(types)
        ]
        return Signature(params)

    def __getattr__(self, name):
        if name == "connect":
            name = self.__class__.__name__
            raise AttributeError(
                f"{name!r} object has no attribute 'connect'. You can connect to the "
                "signal on the *instance* of a class with a Signal() class attribute. "
                "Or create a signal instance directly with SignalInstance."
            )
        return self.__getattribute__(name)

    @overload
    def __get__(self, instance: None, owner: type | None = None) -> Signal:
        ...

    @overload
    def __get__(self, instance: Any, owner: type | None = None) -> SignalInstance:
        ...

    def __get__(self, instance: Any, owner: type = None) -> Signal | SignalInstance:
        # if instance is not None, we're being accessed on an instance of `owner`
        # otherwise we're being accessed on the `owner` itself
        if instance is None:
            return self
        d = self._signal_instances.setdefault(self, weakref.WeakKeyDictionary())
        return d.setdefault(instance, SignalInstance(self.signatures, instance))


class SignalInstance:
    def __init__(
        self, signatures: tuple[Signature, ...] = (Signature(),), instance: Any = None
    ) -> None:
        self.signatures = signatures
        self._instance: object = instance
        self._slots: list[SlotRef] = []
        self._is_blocked: bool = False

    def __getitem__(self, key: object) -> SignalInstance:
        # used to return a version of self that accepts a specific signature
        pass

    # could return handle to the connection?
    def connect(self, slot: CallbackType) -> None:
        if not callable(slot):
            raise TypeError(f"Cannot connect to non-callable object: {slot}")

        for s in sorted(self.signatures, key=lambda x: len(x.parameters), reverse=True):
            if sigs_compatible(slot, s):
                break
        else:
            accepted = ",".join(str(x) for x in self.signatures)
            raise TypeError(
                f"incompatible slot signature: {signature(slot)}. Accepted: {accepted}"
            )

        # TODO: check signature against self._signal.signatures
        # Qt would just append... allowing for multiple connections of the same func?
        self._slots.append(self._normalize_slot(slot))

    def disconnect(self, slot: CallbackType | None = None) -> None:
        if slot is None:
            # NOTE: clearing an empty list is actually a RuntimeError in Qt
            self._slots.clear()
            return

        # Qt behavior:
        # if the same object is connected multiple times,
        # this only removes the first one it finds...
        # Or raises a ValueError if not in the list
        try:
            self._slots.remove(self._normalize_slot(slot))
        except ValueError as e:
            raise ValueError(f"slot is not connected: {slot}") from e

    def emit(self, *args: Any) -> None:
        if self._is_blocked:
            return

        for slot in self._slots:
            if isinstance(slot, weakref.WeakKeyDictionary):
                for obj, func in slot.items():
                    with receiver_sender(obj, self._instance):
                        func(obj, *args[: _get_code(func).co_argcount])
            else:
                # FIXME: for performance reasons, this "argument eating" should be done
                # at connection time, not here, but that makes it a bit harder
                # to know if a given slot is in the list
                slot(*args[: _get_code(slot).co_argcount])

    def block(self, should_block: bool = True):
        """Sets blocking of the signal"""
        self._is_blocked = bool(should_block)

    def blocked(self):
        return SignalBlocker(self)

    def _normalize_slot(self, slot: CallbackType) -> SlotRef:
        if ismethod(slot):
            return weakref.WeakKeyDictionary({slot.__self__: slot.__func__})  # type: ignore
        # XXX: could consider doing weakref if we know its a function (but not lambda!)
        return slot

    def __call__(self, *args):
        self.emit(*args)


class SignalBlocker:
    def __init__(self, target: SignalInstance):
        self.target = target

    def __enter__(self):
        self.target.block(True)

    def __exit__(self, *args):
        self.target.block(False)


class Receiver:
    def get_sender(self):
        return getattr(self, "_sender", None)

    def _set_sender(self, sender):
        self._sender = sender


@contextmanager
def receiver_sender(rcv, sender):
    if not isinstance(rcv, Receiver):
        yield
        return

    rcv._set_sender(sender)
    try:
        yield
    finally:
        rcv._set_sender(None)


# These __code__ inspection methods are faster and more direct than using
# inspect module but probably more error prone.  If bugs pop up, consider switching


def safe_wrap(func):
    """create function that throws out positional arguments that `func` cannot take."""
    max_args = _get_code(func).co_argcount

    @wraps(func)
    def _inner(*args):
        return func(*args[:max_args])

    return _inner


def _get_code(obj):
    func_code = getattr(obj, "__code__", None)
    if not func_code and hasattr(obj, "__call__"):
        func_code = getattr(obj.__call__, "__code__", None)
    return func_code


def _pos_arg_count(func):
    func_code = _get_code(func)
    if not func_code:
        return False

    defaults = getattr(func, "__defaults__", None)
    argcount = func_code.co_argcount

    if not defaults:
        defaults = getattr(func.__call__, "defaults", ())
        # XXX: HACK... test performance against just using inspect directly
        if "self" in func_code.co_varnames or "_mock_self" in func_code.co_varnames:
            argcount -= 1

    n_defaults = len(defaults) if defaults else 0
    return argcount - n_defaults


def _arg_count_compatible(func: Callable[..., None], sig: Signature):
    """Return True if func accepts equal or less positional args than sig"""
    if not callable(func):
        return False
    return _pos_arg_count(func) <= len(sig.parameters)


def _arg_types_compatible(func, sig: Signature, strict_length=False):
    func_code = _get_code(func)
    pos_arg_names = func_code.co_varnames[: func_code.co_argcount]

    if strict_length and len(pos_arg_names) != len(sig.parameters):
        return False

    f_annotations = getattr(func, "__annotations__", {})
    if not f_annotations and hasattr(func, "__call__"):
        f_annotations = getattr(func.__call__, "__annotations__", {})
    if not f_annotations:
        return True

    for name, param in zip(pos_arg_names, sig.parameters.values()):
        annotation = f_annotations.get(name)
        if not annotation or param.annotation is Parameter.empty:
            continue
        if annotation != param.annotation:
            return False
    return True


def sigs_compatible(func, sig, check_types=True):
    if _arg_count_compatible(func, sig):
        return _arg_types_compatible(func, sig) if check_types else True
    return False
