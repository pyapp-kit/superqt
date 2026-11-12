# FAQ

## Sliders not dragging properly on macOS 12+

With Qt 5 on macOS 12 (Monterey) and later, a bug in Qt makes all sliders,
including Qt's own, respond badly to dragging
([QTBUG-98093](https://bugreports.qt.io/browse/QTBUG-98093), and
[superqt#74](https://github.com/pyapp-kit/superqt/issues/74)). Qt 6 doesn't have
this bug.

superqt includes a workaround: a style sheet for the sliders. It isn't perfect,
and it replaces the sliders' styles (so it may interfere with your own; and if
you already style your sliders, you may not see the bug). To use it, do one of
the following:

- Set the environment variable `USE_MAC_SLIDER_PATCH=1` before importing
  superqt. superqt's sliders then use the style sheet if they run with Qt 5 on
  macOS 12 or later (so it's safe to set on other platforms). This applies to all
  of them except `QLabeledSlider`, which contains a plain `QSlider`.
- Call the `applyMacStylePatch()` method of a `QDoubleSlider`, `QRangeSlider`,
  or `QDoubleRangeSlider`. This applies the style sheet whatever the platform,
  and replaces the slider's style sheet.
- Apply the style sheet yourself, to any slider:

    ```python
    from superqt.sliders import MONTEREY_SLIDER_STYLES_FIX

    slider.setStyleSheet(MONTEREY_SLIDER_STYLES_FIX)
    ```
