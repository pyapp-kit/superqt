# Threading decorators

`superqt` provides two decorators that help to ensure that given function is
running in the desired thread:

## `ensure_main_thread`

`ensure_main_thread` ensures that the decorated function/method runs in the main thread

## `ensure_object_thread`

`ensure_object_thread` ensures that a decorated bound method of a `QObject` runs
in the thread in which the instance lives ([see qt documentation for
details](https://doc.qt.io/qt-6/threads-qobject.html#accessing-qobject-subclasses-from-other-threads)).

## Usage

By default, functions are executed asynchronously (they return immediately with
an instance of
[`concurrent.futures.Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future)).

To block and wait for the result, see [Synchronous mode](#synchronous-mode)

```python
from qtpy.QtCore import QObject
from superqt import ensure_main_thread, ensure_object_thread

@ensure_main_thread
def sample_function():
    print("This function will run in main thread")


class SampleObject(QObject):
    def __init__(self):
        super().__init__()
        self._value = 1

    @ensure_main_thread
    def sample_method1(self):
        print("This method will run in main thread")

    @ensure_object_thread
    def sample_method3(self):
        import time
        print("sleeping")
        time.sleep(1)
        print("This method will run in object thread")

    @property
    def value(self):
        print("return value")
        return self._value

    @value.setter
    @ensure_object_thread
    def value(self, value):
        print("this setter will run in object thread")
        self._value = value
```

As can be seen in this example these decorators can also be used for setters.

These decorators should not be used as replacement of Qt Signals but rather to
interact with Qt objects from non Qt code.

## Synchronous mode

If you'd like for the program to block and wait for the result of your function
call, use the `await_return=True` parameter, and optionally specify a timeout.

!!! important

    Using synchronous mode may significantly impact performance.

```python
from superqt import ensure_main_thread

@ensure_main_thread
def sample_function1():
    return 1

@ensure_main_thread(await_return=True)
def sample_function2():
    return 2

assert sample_function1() is None
assert sample_function2() == 2

# optionally, specify a timeout
@ensure_main_thread(await_return=True, timeout=10000)
def sample_function():
    return 1

```
