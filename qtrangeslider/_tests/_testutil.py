from contextlib import suppress
from distutils.version import LooseVersion
from platform import system

import pytest

from qtrangeslider.qtcompat import QT_VERSION
from qtrangeslider.qtcompat.QtCore import QEvent, QPoint, QPointF, Qt
from qtrangeslider.qtcompat.QtGui import QMouseEvent, QWheelEvent

QT_VERSION = LooseVersion(QT_VERSION)

SYS_DARWIN = system() == "Darwin"

skip_on_linux_qt6 = pytest.mark.skipif(
    system() == "Linux" and QT_VERSION >= LooseVersion("6.0"),
    reason="hover events not working on linux pyqt6",
)


def _mouse_event(pos=QPointF(), type_=QEvent.MouseMove):
    """Create a mouse event of `type_` at `pos`."""
    return QMouseEvent(type_, QPointF(pos), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)


def _wheel_event(arc):
    """Create a wheel event with `arc`."""
    with suppress(TypeError):
        return QWheelEvent(
            QPointF(),
            QPointF(),
            QPoint(arc, arc),
            QPoint(arc, arc),
            Qt.NoButton,
            Qt.NoModifier,
            Qt.ScrollBegin,
            False,
            Qt.MouseEventSynthesizedByQt,
        )
    with suppress(TypeError):
        return QWheelEvent(
            QPointF(),
            QPointF(),
            QPoint(-arc, -arc),
            QPoint(-arc, -arc),
            1,
            Qt.Vertical,
            Qt.NoButton,
            Qt.NoModifier,
            Qt.ScrollBegin,
            False,
            Qt.MouseEventSynthesizedByQt,
        )

    return QWheelEvent(
        QPointF(),
        QPointF(),
        QPoint(arc, arc),
        QPoint(arc, arc),
        1,
        Qt.Vertical,
        Qt.NoButton,
        Qt.NoModifier,
    )


def _linspace(start, stop, n):
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i
