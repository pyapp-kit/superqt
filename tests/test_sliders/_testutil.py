from contextlib import suppress
from platform import system

import pytest

from superqt.qtcompat import QT_VERSION
from superqt.qtcompat.QtCore import QEvent, QPoint, QPointF, Qt
from superqt.qtcompat.QtGui import QMouseEvent, QWheelEvent

QT_VERSION = tuple(int(x) for x in QT_VERSION.split("."))

SYS_DARWIN = system() == "Darwin"

skip_on_linux_qt6 = pytest.mark.skipif(
    system() == "Linux" and QT_VERSION >= (6, 0),
    reason="hover events not working on linux pyqt6",
)


def _mouse_event(pos=QPointF(), type_=QEvent.Type.MouseMove):
    """Create a mouse event of `type_` at `pos`."""
    return QMouseEvent(
        type_,
        QPointF(pos),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _wheel_event(arc):
    """Create a wheel event with `arc`."""
    with suppress(TypeError):
        return QWheelEvent(
            QPointF(),
            QPointF(),
            QPoint(arc, arc),
            QPoint(arc, arc),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollBegin,
            False,
            Qt.MouseEventSource.MouseEventSynthesizedByQt,
        )
    with suppress(TypeError):
        return QWheelEvent(
            QPointF(),
            QPointF(),
            QPoint(-arc, -arc),
            QPoint(-arc, -arc),
            1,
            Qt.Orientation.Vertical,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollBegin,
            False,
            Qt.MouseEventSource.MouseEventSynthesizedByQt,
        )

    return QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(arc, arc),
        QPoint(arc, arc),
        1,
        Qt.Orientation.Vertical,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )


def _linspace(start, stop, n):
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i
