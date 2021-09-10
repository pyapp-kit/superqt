# Decorators


## Move to thread decorators

`superqt` provides two decorators for ensure that given function is running in proper thread:

* `ensure_main_thread` - run function/method in main thread
* `ensure_object_thread` - run method of `QObject` instance in thread in which given instance live ([qt documentation](https://doc.qt.io/qt-5/threads-qobject.html#accessing-qobject-subclasses-from-other-threads)).

By default, functions are executed in async mode:

```python
from superqt.qtcompat.QtCore import QObject
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

    @ensure_main_thread()
    def sample_method2(self):
        print("This method also will run in main thread")

    @ensure_object_thread
    def sample_method3(self):
        print("This method will run in object thread")

    @ensure_object_thread()
    def sample_method4(self):
        print("This method also will run in object thread")

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

As visible on example these decorators also could be used for setters.

These decorators should not be used as replacement of Qt Signals but rather to interact with Qt objects from non Qt code.

### Sync mode

Secorators could be used also in sync mode:

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
```

Using sync mode may introduce significant performance impact.

Decorators also provide `timeout` argument (in milliseconds). Works only with `await_return=True`

```python

from superqt import ensure_main_thread

@ensure_main_thread(await_return=True, timeout=1000)
def sample_function():
    return 1
```
