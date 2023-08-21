from __future__ import annotations

import traceback
from contextlib import AbstractContextManager
from types import TracebackType

from qtpy.QtWidgets import QErrorMessage, QMessageBox, QWidget

_GLOBAL_ERR = None


def global_err_message() -> QErrorMessage:
    global _GLOBAL_ERR
    if _GLOBAL_ERR is None:
        _GLOBAL_ERR = QErrorMessage()
    return _GLOBAL_ERR


class exceptions_as_dialog(AbstractContextManager):
    """Context manager that shows a QMessageBox when an exception is raised.

    Example
    -------
    ```python
    with exceptions_as_dialog():
        raise Exception("This will be caught and shown in a QMessageBox")

    with exceptions_as_dialog(ValueError):
        1 / 0  # ZeroDivisionError is not caught, so this will raise

    with exceptions_as_dialog(msg_template="Error: {exc_value}"):
        raise Exception("This message will be used as 'exc_value'")

    for _i in range(3):
        with exceptions_as_dialog(AssertionError, use_global_err_message=True):
            assert False, "Uncheck the checkbox to ignore this in the future"
    ```
    """

    widget: QMessageBox | None
    raised: bool

    def __init__(
        self,
        exceptions: type[BaseException] | tuple[type[BaseException], ...] = (Exception),
        icon: QMessageBox.Icon = QMessageBox.Icon.Critical,
        title: str = "An error occurred",
        msg_template: str = "{exc_value}",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        parent: QWidget | None = None,
        use_global_err_message: bool = False,
    ):
        self.exceptions = exceptions
        self.msg_template = msg_template
        self.use_global_err_message = use_global_err_message
        self.raised = False
        if not use_global_err_message:
            self.widget = QMessageBox(icon, title, "", buttons, parent)
        else:
            self.widget = None

    def __enter__(self) -> exceptions_as_dialog:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if not (exc_value is not None and isinstance(exc_value, self.exceptions)):
            return False  # let it propagate

        self.raised = True
        if "{tb}" in self.msg_template:
            _tb = "\n".join(traceback.format_exception(exc_type, exc_value, tb))
        else:
            _tb = ""
        text = self.msg_template.format(exc_value=exc_value, exc_type=exc_type, tb=_tb)

        if self.use_global_err_message:
            global_err_message().showMessage(text)
        elif self.widget is not None:
            self.widget.setText(text)
            self.widget.exec()  # could use the result to re-raise the exception

        return True  # swallow the exception
