import logging

from superqt import QMessageHandler
from superqt.qtcompat import QtCore


def test_message_handler():
    with QMessageHandler() as mh:
        QtCore.qDebug("debug")
        QtCore.qWarning("warning")
        QtCore.qCritical("critical")

    assert len(mh.records) == 3
    assert mh.records[0].level == logging.DEBUG
    assert mh.records[1].level == logging.WARNING
    assert mh.records[2].level == logging.CRITICAL

    assert "3 records" in repr(mh)


def test_message_handler_with_logger(caplog):
    logger = logging.getLogger("test_logger")
    caplog.set_level(logging.DEBUG, logger="test_logger")
    with QMessageHandler(logger):
        QtCore.qDebug("debug")
        QtCore.qWarning("warning")
        QtCore.qCritical("critical")

    assert len(caplog.records) == 3
    caplog.records[0].message == "debug"
    caplog.records[0].levelno == logging.DEBUG
    caplog.records[1].message == "warning"
    caplog.records[1].levelno == logging.WARNING
    caplog.records[2].message == "critical"
    caplog.records[2].levelno == logging.CRITICAL
