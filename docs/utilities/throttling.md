# Throttling & Debouncing

These utilities allow you to throttle or debounce a function. This is useful
when you have a function that is called multiple times in a short period of
time, and you want to make sure it is only "actually" called once (or at least
no more than a certain frequency).

For background on throttling and debouncing, see:

- <https://blog.openreplay.com/forever-functional-debouncing-and-throttling-for-performance>
- <https://css-tricks.com/debouncing-throttling-explained-examples/>

::: superqt.utils.qdebounced
    options:
        show_source: false
        docstring_style: numpy
        show_root_toc_entry: True
        show_root_heading: True

::: superqt.utils.qthrottled
    options:
        show_source: false
        docstring_style: numpy
        show_root_toc_entry: True
        show_root_heading: True

::: superqt.utils.QSignalDebouncer
    options:
        show_source: false
        docstring_style: numpy
        show_root_toc_entry: True
        show_root_heading: True

::: superqt.utils.QSignalThrottler
    options:
        show_source: false
        docstring_style: numpy
        show_root_toc_entry: True
        show_root_heading: True

::: superqt.utils._throttler.GenericSignalThrottler
    options:
        show_source: false
        docstring_style: numpy
        show_root_toc_entry: True
        show_root_heading: True


## Throttling and tests.

The throttlers are using internally timers to schedule proper calls. It is helpful
in normal usage but may be problematic in tests. To avoid this problem, this package
provides `disable_throttling` fixture that disables all throttlers and debouncers.
The effect is that signals are emitted immediately and the timer is not used.
