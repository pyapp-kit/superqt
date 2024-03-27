from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, cast

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QErrorMessage, QMessageBox, QWidget

if TYPE_CHECKING:
    from types import TracebackType


_DEFAULT_FLAGS = Qt.WindowType.Dialog | Qt.WindowType.MSWindowsFixedSizeDialogHint


class exceptions_as_dialog:
    """Context manager that shows a dialog when an exception is raised.

    See examples below for common usage patterns.

    To determine whether an exception was raised or not, check the `exception`
    attribute after the context manager has exited.  If `use_error_message` is `False`
    (the default), you can also access the `dialog` attribute to get/manipulate the
    `QMessageBox` instance.

    Parameters
    ----------
    exceptions : type[BaseException] | tuple[type[BaseException], ...], optional
        The exception(s) to catch, by default `Exception` (i.e. all exceptions).
    icon : QMessageBox.Icon, optional
        The icon to show in the QMessageBox, by default `QMessageBox.Icon.Critical`
    title : str, optional
        The title of the `QMessageBox`, by default `"An error occurred"`.
    msg_template : str, optional
        The message to show in the `QMessageBox`. The message will be formatted
        using three variables:

        - `exc_value`: the exception instance
        - `exc_type`: the exception type
        - `tb`: the traceback as a string

        The default template is the content of the exception: `"{exc_value}"`
    buttons : QMessageBox.StandardButton, optional
        The buttons to show in the `QMessageBox`, by default
        `QMessageBox.StandardButton.Ok`
    parent : QWidget | None, optional
        The parent widget of the `QMessageBox`, by default `None`
    use_error_message : bool | QErrorMessage, optional
        Whether to use a `QErrorMessage` instead of a `QMessageBox`. By default
        `False`. `QErrorMessage` shows a checkbox that the user can check to
        prevent seeing the message again (based on the text of the formatted
        `msg_template`.) If `True`, the global `QMessageError.qtHandler()`
        instance is used to maintain a history of dismissed messages. You may also pass
        a `QErrorMessage` instance to use a specific instance. If `use_error_message` is
        True, or if you pass your own `QErrorMessage` instance, the `parent` argument
        is ignored.

    Attributes
    ----------
    dialog : QMessageBox | None
        The `QMessageBox` instance that was created (if `use_error_message` was
        `False`).  This can be used, among other things, to determine the result of
        the dialog (e.g. `dialog.result()`) or to manipulate the dialog (e.g.
        `dialog.setDetailedText("some text")`).
    exception : BaseException | None
        Will hold the exception instance if an exception was raised and caught.

    Examples
    --------
    ```python
    from qtpy.QtWidgets import QApplication
    from superqt.utils import exceptions_as_dialog

    app = QApplication([])

    with exceptions_as_dialog() as ctx:
        raise Exception("This will be caught and shown in a QMessageBox")

    # you can access the exception instance here
    assert ctx.exception is not None

    # with exceptions_as_dialog(ValueError):
    #     1 / 0  # ZeroDivisionError is not caught, so this will raise

    with exceptions_as_dialog(msg_template="Error: {exc_value}"):
        raise Exception("This message will be inserted at 'exc_value'")

    for _i in range(3):
        with exceptions_as_dialog(AssertionError, use_error_message=True):
            assert False, "Uncheck the checkbox to ignore this in the future"

    # use ctx.dialog to get the result of the dialog
    btns = QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
    with exceptions_as_dialog(buttons=btns) as ctx:
        raise Exception("This will be caught and shown in a QMessageBox")
    print(ctx.dialog.result())  # prints which button was clicked

    app.exec()  # needed only for the use_error_message example to show
    ```
    """

    dialog: QMessageBox | None
    exception: BaseException | None
    exec_result: int | None = None

    def __init__(
        self,
        exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception,
        icon: QMessageBox.Icon = QMessageBox.Icon.Critical,
        title: str = "An error occurred",
        msg_template: str = "{exc_value}",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        parent: QWidget | None = None,
        flags: Qt.WindowType = _DEFAULT_FLAGS,
        use_error_message: bool | QErrorMessage = False,
    ):
        self.exceptions = exceptions
        self.msg_template = msg_template
        self.exception = None
        self.dialog = None

        self._err_msg = use_error_message

        if not use_error_message:
            # the message will be overwritten in __exit__
            self.dialog = QMessageBox(
                icon, title, "An error occurred", buttons, parent, flags
            )

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

        # save the exception for later
        self.exception = exc_value

        # format the message using the context variables
        if "{tb}" in self.msg_template:
            _tb = "\n".join(traceback.format_exception(exc_type, exc_value, tb))
        else:
            _tb = ""
        text = self.msg_template.format(exc_value=exc_value, exc_type=exc_type, tb=_tb)

        # show the dialog
        if self._err_msg:
            msg = (
                self._err_msg
                if isinstance(self._err_msg, QErrorMessage)
                else QErrorMessage.qtHandler()
            )
            cast("QErrorMessage", msg).showMessage(text)
        elif self.dialog is not None:  # it won't be if use_error_message=False
            self.dialog.setText(text)
            self.dialog.exec()

        return True  # swallow the exception
