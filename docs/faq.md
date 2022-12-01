# FAQ

## Sliders not dragging properly on MacOS 12+

??? details
    On MacOS Monterey, with Qt5, there is a bug that causes all sliders
    (including native Qt sliders) to not respond properly to drag events.  See:

    - [https://bugreports.qt.io/browse/QTBUG-98093](https://bugreports.qt.io/browse/QTBUG-98093)
    - [https://github.com/pyapp-kit/superqt/issues/74](https://github.com/pyapp-kit/superqt/issues/74)

    Superqt includes a workaround for this issue, but it is not perfect, and it requires using a custom stylesheet (which may interfere with your own styles).  Note that you
    may not see this issue if you're already using custom stylesheets.

    To opt in to the workaround, do any of the following:

    - set the environment variable `USE_MAC_SLIDER_PATCH=1` before importing superqt
    (note: this is safe to use even if you're targeting more than just MacOS 12, it will only be applied when needed)
    - call the `applyMacStylePatch()` method on any of the superqt slider subclasses (note, this will override your slider styles)
    - apply the stylesheet manually:

    ```python
    from superqt.sliders import MONTEREY_SLIDER_STYLES_FIX

    slider.setStyleSheet(MONTEREY_SLIDER_STYLES_FIX)
    ```
