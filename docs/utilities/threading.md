# Thread workers

Workers run a long task in another thread, so that the GUI stays responsive,
and report back with signals (such as `started`, `returned`, `errored`,
`finished`, and, for generators, `yielded`), which can safely update the GUI
from the main thread. Except for
`new_worker_qthread`, they use Qt's
[`QRunnable`](https://doc.qt.io/qt-6/qrunnable.html) and global
[`QThreadPool`](https://doc.qt.io/qt-6/qthreadpool.html).

The simplest way to use them is the
[`@thread_worker`][superqt.utils.thread_worker] decorator. Calling a decorated
function returns a worker, which runs the function when it's started (or at
once, if callbacks are given with `connect=`):

```python
import time

from superqt.utils import thread_worker


@thread_worker
def long_task(n):
    time.sleep(n)
    return n


worker = long_task(2)
worker.returned.connect(print)
worker.start()
```

If the function is a generator, the worker is a
[`GeneratorWorker`][superqt.utils.GeneratorWorker]: it emits `yielded` for each
value, and can be paused, resumed, and aborted between them. Otherwise, it's a
[`FunctionWorker`][superqt.utils.FunctionWorker].

These tools were written for napari, and moved to superqt. The
[napari guide to threading](https://napari.org/stable/guides/threading.html#threading-in-napari-with-thread-worker)
describes them in more depth.

::: superqt.utils.WorkerBase

::: superqt.utils.FunctionWorker

::: superqt.utils.GeneratorWorker

## Convenience functions

::: superqt.utils.thread_worker
    options:
        heading_level: 3

::: superqt.utils.create_worker
    options:
        heading_level: 3

::: superqt.utils.new_worker_qthread
    options:
        heading_level: 3
