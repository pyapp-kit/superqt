import os
import sys
from unittest.mock import Mock

import pytest
import qtpy
from qtpy.QtCore import QObject, QTimer, Signal
from qtpy.QtWidgets import QApplication, QErrorMessage, QMessageBox

from superqt.utils import exceptions_as_dialog, signals_blocked
from superqt.utils._util import get_max_args


def test_signal_blocker(qtbot):
    """make sure context manager signal blocker works"""

    class Emitter(QObject):
        sig = Signal()

    obj = Emitter()
    receiver = Mock()
    obj.sig.connect(receiver)

    # make sure signal works
    with qtbot.waitSignal(obj.sig):
        obj.sig.emit()

    receiver.assert_called_once()
    receiver.reset_mock()

    with signals_blocked(obj):
        obj.sig.emit()
        qtbot.wait(10)

    receiver.assert_not_called()


def test_get_max_args_simple():
    def fun1():
        pass

    assert get_max_args(fun1) == 0

    def fun2(a):
        pass

    assert get_max_args(fun2) == 1

    def fun3(a, b=1):
        pass

    assert get_max_args(fun3) == 2

    def fun4(a, *, b=2):
        pass

    assert get_max_args(fun4) == 1

    def fun5(a, *b):
        pass

    assert get_max_args(fun5) is None

    assert get_max_args(print) is None


def test_get_max_args_wrapped():
    from functools import partial, wraps

    def fun1(a, b):
        pass

    assert get_max_args(partial(fun1, 1)) == 1

    def dec(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)

        return wrapper

    assert get_max_args(dec(fun1)) == 2


def test_get_max_args_methods():
    class A:
        def fun1(self):
            pass

        def fun2(self, a):
            pass

        def __call__(self, a, b=1):
            pass

    assert get_max_args(A().fun1) == 0
    assert get_max_args(A().fun2) == 1
    assert get_max_args(A()) == 2


MAC_CI_PYSIDE6 = bool(
    sys.platform == "darwin" and os.getenv("CI") and qtpy.API_NAME == "PySide6"
)


@pytest.mark.skipif(MAC_CI_PYSIDE6, reason="still hangs on mac ci with pyside6")
def test_exception_context(qtbot, qapp: QApplication) -> None:
    def accept():
        for wdg in qapp.topLevelWidgets():
            if isinstance(wdg, QMessageBox):
                wdg.button(QMessageBox.StandardButton.Ok).click()

    with exceptions_as_dialog():
        QTimer.singleShot(0, accept)
        raise Exception("This will be caught and shown in a QMessageBox")

    with pytest.raises(ZeroDivisionError), exceptions_as_dialog(ValueError):
        1 / 0  # noqa

    with exceptions_as_dialog(msg_template="Error: {exc_value}"):
        QTimer.singleShot(0, accept)
        raise Exception("This message will be used as 'exc_value'")

    err = QErrorMessage()
    with exceptions_as_dialog(use_error_message=err):
        QTimer.singleShot(0, err.accept)
        raise AssertionError("Uncheck the checkbox to ignore this in the future")

    # tb formatting smoke test, and return value checking
    exc = ValueError("Bad Val")
    with exceptions_as_dialog(
        msg_template="{tb}",
        buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
    ) as ctx:
        qtbot.addWidget(ctx.dialog)
        QTimer.singleShot(100, accept)
        raise exc

    assert isinstance(ctx.dialog, QMessageBox)
    assert ctx.dialog.result() == QMessageBox.StandardButton.Ok
    assert ctx.exception is exc
