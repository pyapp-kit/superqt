from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator
from unittest.mock import patch

from qtpy.QtCore import QObject, SignalInstance

if TYPE_CHECKING:
    from qtpy.QtCore import QMetaObject


@contextmanager
def signals_blocked(obj: "QObject") -> Iterator[None]:
    """Context manager to temporarily block signals emitted by QObject: `obj`.

    Parameters
    ----------
    obj : QObject
        The QObject whose signals should be blocked.

    Examples
    --------
    ```python
    from qtpy.QtWidgets import QSpinBox
    from superqt import signals_blocked

    spinbox = QSpinBox()
    with signals_blocked(spinbox):
        spinbox.setValue(10)
    ```
    """
    previous = obj.blockSignals(True)
    try:
        yield
    finally:
        obj.blockSignals(previous)


CONNECT = SignalInstance.connect


class connection_token:
    """Context manager in which all connections are stored for later disconnection.

    This provides a convenient way to remember a number of connections for easy
    disconnection later.

    Examples
    --------
    ```python
    from qtpy.QtCore import QObject, Signal
    from superqt.utils import connection_token

    class Thing(QObject):
        sig = Signal(int)

    t = Thing()
    with connection_token() as token:
        t.sig.connect(lambda v: print("called with", v))
        t.sig.connect(lambda: print("hey!"))
        t.sig.connect(lambda: print("anyone there?"))

    t.sig.emit(2)  # prints a bunch of stuff

    token.disconnect()
    t.sig.emit(4)  # nothing happens
    ```
    """

    def __init__(self) -> None:
        self._connections: list[QMetaObject.Connection] = []

        # will be mocked in for SignalInstance.connect
        def _store_connection(*args, **kwargs):
            # perform the connection
            connection = CONNECT(*args, **kwargs)
            # store the connection for later disconnection
            self.append(connection)
            return connection

        # create a patcher for SignalInstance.connect
        self._patch_connect = patch.object(SignalInstance, "connect", _store_connection)

    def __enter__(self) -> "connection_token":
        """Start the patcher."""
        self._patch_connect.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop the patcher."""
        self._patch_connect.stop()

    def __len__(self) -> int:
        return len(self._connections)

    def append(self, connection: QMetaObject.Connection) -> None:
        """Manually store a connection."""
        self._connections.append(connection)

    def disconnect(self) -> None:
        """Disconnect all connections stored in this token."""
        while self._connections:
            QObject.disconnect(self._connections.pop())


@contextmanager
def temporary_connections() -> Iterator[connection_token]:
    """Context in which all signal/slot connections are temporary.

    Examples
    --------
    ```python
    from superqt.utils import temporary_connections

    with temporary_connections():
        obj.some_signal.connect(some_callback)
        obj.some_signal.emit()  # some_callback is called
    obj.some_signal.emit()  # some_callback is not called
    ```
    """
    with connection_token() as token:
        yield token
    token.disconnect()
