from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from qtpy.QtCore import QObject


@contextmanager
def signals_blocked(obj: "QObject") -> Iterator[None]:
    """Context manager to temporarily block signals emitted by QObject: `obj`."""
    previous = obj.blockSignals(True)
    try:
        yield
    finally:
        obj.blockSignals(previous)
