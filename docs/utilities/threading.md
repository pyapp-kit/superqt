# Thread workers

The objects in this module provide utilities for running tasks in a separate
thread. In general (with the exception of `new_worker_qthread`), everything
here wraps Qt's [QRunnable API](https://doc.qt.io/qt-6/qrunnable.html).

The highest level object is the
[`@thread_worker`][superqt.utils.thread_worker] decorator.  It was originally
written for `napari`, and was later extracted into `superqt`.  You may also be
interested in reading the [napari
documentation](https://napari.org/stable/guides/threading.html#threading-in-napari-with-thread-worker) on this feature,
which provides a more in-depth/introductory usage guide.

For additional control, you can create your own
[`FunctionWorker`][superqt.utils.FunctionWorker] or
[`GeneratorWorker`][superqt.utils.GeneratorWorker] objects.

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
