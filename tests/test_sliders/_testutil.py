from contextlib import suppress
from platform import system

import pytest
from qtpy import QT_VERSION
from qtpy.QtCore import QEvent, QPoint, QPointF, Qt
from qtpy.QtGui import QHoverEvent, QMouseEvent, QWheelEvent

QT_VERSION = tuple(int(x) for x in QT_VERSION.split("."))

SYS_DARWIN = system() == "Darwin"

skip_on_linux_qt6 = pytest.mark.skipif(
    system() == "Linux" and QT_VERSION >= (6, 0),
    reason="hover events not working on linux pyqt6",
)

_PointF = QPointF()


def _mouse_event(pos=_PointF, type_=QEvent.Type.MouseMove):
    """Create a mouse event of `type_` at `pos`."""
    return QMouseEvent(
        type_,
        QPointF(pos),  # localPos
        QPointF(),  # windowPos / globalPos
        Qt.MouseButton.LeftButton,  # button
        Qt.MouseButton.LeftButton,  # buttons
        Qt.KeyboardModifier.NoModifier,  # modifiers
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


def _hover_event(_type, position, old_position, widget=None):
    with suppress(TypeError):
        return QHoverEvent(
            _type,
            position,
            widget.mapToGlobal(position),
            old_position,
        )
    return QHoverEvent(_type, position, old_position)


def _linspace(start: int, stop: int, n: int):
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i
