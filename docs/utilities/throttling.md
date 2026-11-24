# Throttling and debouncing

When a function is called many times in quick succession (for example, by a
slider's `valueChanged` signal while it's dragged), throttling and debouncing
limit how often it actually runs:

- **Throttling** runs it at most once per timeout. With the default (leading)
  policy, the first call runs at once, and further calls during the timeout are
  combined into one call at its end.
- **Debouncing** waits until the calls have stopped for the timeout, and then
  runs it once.

Below, a slider's `valueChanged` signal is connected to a function directly, and
to the same function decorated with `qthrottled` and with `qdebounced`. Each
tick is a call, and the value is what the last call received:

{{ show_widget("throttling") }}

??? example "The code for this demo"

    ```python
    --8<--
    examples/throttling.py
    --8<--
    ```

For more background, see
[Debouncing and throttling explained](https://css-tricks.com/debouncing-throttling-explained-examples/).

The `qthrottled` and `qdebounced` decorators wrap a function:

```python
from superqt.utils import qdebounced, qthrottled


@qthrottled(timeout=100)  # milliseconds
def update_preview(value): ...


@qdebounced(timeout=300)
def save_settings(value): ...


slider.valueChanged.connect(update_preview)
slider.valueChanged.connect(save_settings)
```

The decorated function is called with the arguments of the last call that it
combined. The `QSignalThrottler` and `QSignalDebouncer` objects do the same for
signals: connect a signal to their `throttle()` slot, and their `triggered`
signal is emitted at the throttled (or debounced) rate:

```python
from superqt.utils import QSignalThrottler

throttler = QSignalThrottler()
throttler.setTimeout(100)
slider.valueChanged.connect(throttler.throttle)
throttler.triggered.connect(update_view)
```

::: superqt.utils.qthrottled

::: superqt.utils.qdebounced

::: superqt.utils.QSignalThrottler

::: superqt.utils.QSignalDebouncer

::: superqt.utils._throttler.GenericSignalThrottler
