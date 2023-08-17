from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from qtpy.QtCore import QObject


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
