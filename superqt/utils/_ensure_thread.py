# https://gist.github.com/FlorianRhiem/41a1ad9b694c14fb9ac3

from superqt.qtcompat.QtCore import (
    QCoreApplication,
    QEventLoop,
    QMetaObject,
    QObject,
    Qt,
    QThread,
    QTimer,
    Signal,
    Slot,
)


class CallCallable(QObject):
    finished = Signal(object)
    instances = []

    def __init__(self, callable, *args, **kwargs):
        super().__init__()
        self._callable = callable
        self._args = args
        self._kwargs = kwargs
        CallCallable.instances.append(self)

    @Slot
    def call(self):
        CallCallable.instances.remove(self)
        res = self._callable(*self._args, **self._kwargs)
        self.finished.emit(res)


def ensure_main_thread(func, no_return=True, timeout=1000):
    def _func(*args, **kwargs):
        if QCoreApplication.instance().thread() == QThread.currentThread():
            return func(*args, **kwargs)
        f = CallCallable(func, *args, **kwargs)
        f.moveToThread(QCoreApplication.instance().thread())
        if no_return:
            QMetaObject.invokeMethod(f, "call", Qt.QueuedConnection)
            return

        res = []

        def set_res(data):
            res.append(data)

        f.finished.connect(set_res)
        timer = QTimer()
        timer.setSingleShot(True)
        loop = QEventLoop()
        f.finished.connect(loop.quit)
        timer.timeout.connect(loop.quit)
        timer.start(timeout)
        QMetaObject.invokeMethod(f, "call", Qt.QueuedConnection)
        loop.exec_()
        if len(res) == 0:
            raise TimeoutError("Not recived value")
        return res[0]

    return _func
