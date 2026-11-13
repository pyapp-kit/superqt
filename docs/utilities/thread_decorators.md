# Threading decorators

Qt objects must generally be used from the thread they live in, and widgets
from the main (GUI) thread. These two decorators make a function run in the
right thread, whichever thread calls it:

`ensure_main_thread`
:   Runs the decorated function, or method, in the main thread.

`ensure_object_thread`
:   Runs the decorated method of a `QObject` in the thread that the object lives
    in (see Qt's [threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html#accessing-qobject-subclasses-from-other-threads)).

They're meant for calling Qt code from code that doesn't use Qt (such as a
callback from another library's thread). Between Qt objects, signals and slots
already do this.

## Usage

When called from another thread, the decorated function is queued to run in
its target thread, and the call returns a
[`concurrent.futures.Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future)
at once. (When called from the target thread, the function runs right away, and
the `Future` it returns is already done.)

```python
from qtpy.QtCore import QObject

from superqt import ensure_main_thread, ensure_object_thread


@ensure_main_thread
def update_label(text):
    print("this runs in the main thread")


class Counter(QObject):
    def __init__(self):
        super().__init__()
        self._value = 1

    @ensure_main_thread
    def show(self):
        print("this runs in the main thread")

    @ensure_object_thread
    def reset(self):
        print("this runs in the thread that the Counter lives in")

    @property
    def value(self):
        return self._value

    @value.setter
    @ensure_object_thread
    def value(self, value):
        print("setters work too")
        self._value = value
```

## Waiting for the result

To wait for the function to finish, and get its return value, pass
`await_return=True`. It waits for at most `timeout` milliseconds (1000 by
default), and then raises a `TimeoutError`.

!!! warning

    The calling thread is blocked while it waits.

```python
from concurrent.futures import Future

from superqt import ensure_main_thread


@ensure_main_thread
def get_one():
    return 1


@ensure_main_thread(await_return=True)
def get_two():
    return 2


@ensure_main_thread(await_return=True, timeout=10000)
def get_three():
    return 3


assert isinstance(get_one(), Future)
assert get_two() == 2
assert get_three() == 3
```

## API

::: superqt.utils.ensure_main_thread
    options:
      heading_level: 3

::: superqt.utils.ensure_object_thread
    options:
      heading_level: 3
