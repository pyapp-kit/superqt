from __future__ import annotations

import logging
from contextlib import suppress
from typing import ClassVar, NamedTuple

from qtpy.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler


class Record(NamedTuple):
    level: int
    message: str
    ctx: dict


class QMessageHandler:
    """A context manager to intercept messages from Qt.

    Parameters
    ----------
    logger : logging.Logger, optional
        If provided, intercepted messages will be logged with `logger` at the
        corresponding python log level, by default None

    Attributes
    ----------
    records: list of tuple
        Captured messages. This is a 3-tuple of:
        `(log_level: int, message: str, context: dict)`

    Examples
    --------
    >>> handler = QMessageHandler()
    >>> handler.install()  # now all Qt output will be available at mh.records

    >>> with QMessageHandler() as handler:  # temporarily install
    ...     ...

    >>> logger = logging.getLogger(__name__)
    >>> with QMessageHandler(logger):  # re-reoute Qt messages to a python logger.
    ...     ...
    """

    _qt2loggertype: ClassVar[dict[QtMsgType, int]] = {
        QtMsgType.QtDebugMsg: logging.DEBUG,
        QtMsgType.QtInfoMsg: logging.INFO,
        QtMsgType.QtWarningMsg: logging.WARNING,
        QtMsgType.QtCriticalMsg: logging.ERROR,  # note
        QtMsgType.QtFatalMsg: logging.CRITICAL,  # note
        QtMsgType.QtSystemMsg: logging.CRITICAL,
    }

    def __init__(self, logger: logging.Logger | None = None):
        self.records: list[Record] = []
        self._logger = logger
        self._previous_handler: object | None = "__uninstalled__"

    def install(self):
        """Install this handler (override the current QtMessageHandler)."""
        self._previous_handler = qInstallMessageHandler(self)

    def uninstall(self):
        """Uninstall this handler, restoring the previous handler."""
        if self._previous_handler != "__uninstalled__":
            qInstallMessageHandler(self._previous_handler)

    def __repr__(self):
        n = type(self).__name__
        return f"<{n} object at {hex(id(self))} with {len(self.records)} records>"

    def __enter__(self):
        """Enter a context with this handler installed."""
        self.install()
        return self

    def __exit__(self, *args):
        self.uninstall()

    def __call__(self, msgtype: QtMsgType, context: QMessageLogContext, message: str):
        level = self._qt2loggertype[msgtype]

        # PyQt seems to throw an error if these are simply empty
        ctx = dict.fromkeys(["category", "file", "function", "line"])
        with suppress(UnicodeDecodeError):
            ctx["category"] = context.category
        with suppress(UnicodeDecodeError):
            ctx["file"] = context.file
        with suppress(UnicodeDecodeError):
            ctx["function"] = context.function
        with suppress(UnicodeDecodeError):
            ctx["line"] = context.line

        self.records.append(Record(level, message, ctx))
        if self._logger is not None:
            self._logger.log(level, message, extra=ctx)
