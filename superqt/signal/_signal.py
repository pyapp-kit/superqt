from __future__ import annotations

import weakref
from contextlib import contextmanager
from inspect import Parameter, Signature, ismethod, signature
from typing import TYPE_CHECKING, Any, Callable, Sequence, Union, overload

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
            self.signatures = (Signal._build_signature(types),)
        else:
            # multiple signatures
            _signatures: list[Signature] = []
            for t in types:
                if isinstance(t, Signature):
                    _signatures.append(t)
                elif isinstance(t, (list, tuple)):
                    _signatures.append(Signal._build_signature(t))
                else:
                    raise TypeError(
                        "each signature in a multi-signature sequence must be "
                        "experessed as a Signature, list, or tuple"
                    )
            self.signatures = tuple(_signatures)

    @staticmethod
    def _build_signature(types: Sequence[type]) -> Signature:
        return Signature(
            [
                Parameter(name=f"a{i}", kind=Parameter.POSITIONAL_ONLY, annotation=t)
                for i, t in enumerate(types)
            ]
        )

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

        # TODO: this only checks the number of args not the type
        slot_sig = signature(slot)
        if not any(sigs_compatible(slot_sig, s) for s in self.signatures):
            accepted = ",".join(str(x) for x in self.signatures)
            raise TypeError(
                f"incompatible slot signature: {slot_sig}. Accepted: {accepted}"
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
            self._call_slot(slot, *args)

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

    def _call_slot(self, slot: SlotRef, *args: Any) -> None:
        if isinstance(slot, weakref.WeakKeyDictionary):
            for obj, func in slot.items():
                with receiver_sender(obj, self._instance):
                    func(obj, *args)
        else:
            slot(*args)

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


def sigs_compatible(sig1: Signature, sig2: Signature):
    try:
        sig1.bind(*sig2.parameters)
        return True
    except TypeError:
        return False
