# QMessageHandler

A context manager that captures the messages that Qt logs (with `qDebug`,
`qWarning`, `qCritical`, and so on), instead of printing them, for example to
check for them in tests, or to send them to Python's `logging`.

::: superqt.utils.QMessageHandler
    options:
      heading_level: 2
