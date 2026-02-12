from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qtpy.QtCore import QObject


@contextmanager
def signals_blocked(*obj: "QObject") -> Iterator[None]:
    """Context manager to temporarily block signals emitted by QObjects.

    Parameters
    ----------
    *obj : QObject
        QObjects whose signals should be blocked.

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
    previous = [o.blockSignals(True) for o in obj]
    try:
        yield
    finally:
        for o, prev in zip(obj, previous):
            o.blockSignals(prev)
