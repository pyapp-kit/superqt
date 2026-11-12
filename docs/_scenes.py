"""How each docs example is captured, and the animations recorded for some.

Examples without an entry here are captured as shown, without animation. A scene
receives a `Recorder` (see `_media.py`) and the window that the example shows;
`r.wait(...)` holds still, everything else moves the cursor or types.
Scenes should end where they start, so the animation loops smoothly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from _media import scene, spec
from qtpy.QtCore import QPoint, Qt
from qtpy.QtWidgets import QComboBox, QSlider, QStyle, QStyleOptionSlider

from superqt import (
    QColormapComboBox,
    QLabeledRangeSlider,
    QSearchableComboBox,
    QToggleSwitch,
)

if TYPE_CHECKING:
    from _media import Recorder
    from qtpy.QtWidgets import QWidget

# ---------------------------------------------------------------------------
# Sliders


def _handle(slider: QSlider, index: int = 0) -> QPoint:
    """Center of a slider handle."""
    if hasattr(slider, "_handleRect"):  # range sliders
        return slider._handleRect(index).center()
    if hasattr(slider, "_styleOption"):  # superqt float sliders
        opt = slider._styleOption
    else:
        opt = QStyleOptionSlider()
        slider.initStyleOption(opt)
    cc, sc = QStyle.ComplexControl.CC_Slider, QStyle.SubControl.SC_SliderHandle
    return slider.style().subControlRect(cc, opt, sc, slider).center()


def _drag_handle(r: Recorder, slider: QSlider, index: int, fraction: float) -> None:
    start = _handle(slider, index)
    end = start + QPoint(round(slider.width() * fraction), 0)
    r.drag(slider, start, end, duration=0.7)
    r.wait(0.3)


def _range_scene(r: Recorder, window: QWidget) -> None:
    slider = getattr(window, "_slider", window)  # labeled sliders wrap a slider
    _drag_handle(r, slider, 0, 0.25)
    # drag the bar between the handles, then the upper handle back
    bar = (_handle(slider, 0) + _handle(slider, 1)) / 2
    r.drag(slider, bar, bar - QPoint(round(slider.width() * 0.25), 0), duration=0.8)
    r.wait(0.3)
    _drag_handle(r, slider, 1, 0.25)
    r.leave()


def _single_scene(r: Recorder, window: QWidget) -> None:
    slider = getattr(window, "_slider", window)
    _drag_handle(r, slider, 0, 0.3)
    _drag_handle(r, slider, 0, -0.3)
    r.leave()


SLIDER_WIDTH = 480
for name in ("qrangeslider", "qdoublerangeslider"):
    spec(name, width=SLIDER_WIDTH, scene=_range_scene)
for name in ("qlabeledrangeslider", "qlabeleddoublerangeslider"):
    spec(name, width=SLIDER_WIDTH, scene=_range_scene)
for name in ("qdoubleslider", "qlabeledslider", "qlabeleddoubleslider"):
    spec(name, width=SLIDER_WIDTH, scene=_single_scene)


# ---------------------------------------------------------------------------
# Buttons, containers and layouts


@scene("qtoggleswitch")
def _(r: Recorder, window: QWidget) -> None:
    r.click(window, QPoint(22, window.height() // 2))
    r.wait(0.8)
    r.click(window, QPoint(22, window.height() // 2), duration=0.2)
    r.leave()


@scene("qcollapsible", width=340)
def _(r: Recorder, window: QWidget) -> None:
    button = window.toggleButton()
    r.click(button, QPoint(60, button.height() // 2))
    r.wait(0.9)
    r.click(button, QPoint(60, button.height() // 2), duration=0.2)
    r.wait(0.6)
    r.leave()


@scene("qelidinglabel", width=300)
def _(r: Recorder, window: QWidget) -> None:
    r.resize(150, duration=1.2)
    r.wait(0.5)
    r.resize(300, duration=1.2)


@scene("qflowlayout", width=340)
def _(r: Recorder, window: QWidget) -> None:
    r.resize(170, duration=1.4, fit_height=True)
    r.wait(0.5)
    r.resize(340, duration=1.4, fit_height=True)


# ---------------------------------------------------------------------------
# Searchable widgets


@scene("qsearchablelistwidget", width=260, height=200)
def _(r: Recorder, window: QWidget) -> None:
    r.click(window.filter_widget)
    r.leave(duration=0.3)
    r.type(window.filter_widget, "bar")
    r.wait(0.9)
    r.key(window.filter_widget, Qt.Key.Key_Backspace, times=3)


@scene("qsearchabletreewidget", width=320, height=260)
def _(r: Recorder, window: QWidget) -> None:
    r.click(window.filter)
    r.leave(duration=0.3)
    r.type(window.filter, "fl")
    r.wait(0.9)
    r.key(window.filter, Qt.Key.Key_Backspace, times=2)


@scene("qsearchablecombobox", width=200)
def _(r: Recorder, window: QComboBox) -> None:
    edit = window.lineEdit()
    r.click(edit)
    edit.selectAll()
    r.leave(duration=0.3)
    r.type(edit, "baz")
    r.wait(0.6)
    _complete(r, window)
    r.wait(1.0)
    window.setCurrentIndex(0)
    edit.clearFocus()


def _complete(r: Recorder, combo: QComboBox) -> None:
    """Pick the first completion, with the keyboard."""
    popup = combo.completer().popup()
    r.key(popup, Qt.Key.Key_Down, interval=0.3)
    r.key(popup, Qt.Key.Key_Return)


# ---------------------------------------------------------------------------
# Combo boxes: open the popup and pick an item


def _pick(r: Recorder, combo: QComboBox, index: int) -> None:
    initial = combo.currentIndex()
    r.click(combo)
    r.wait(0.3)
    view = combo.view()
    r.move(view, view.visualRect(combo.model().index(index, 0)).center())
    r.wait(0.3)
    r.press()
    r.release()
    r.wait(0.8)
    r.leave()
    combo.setCurrentIndex(initial)


@scene("qenumcombobox", width=200)
def _(r: Recorder, window: QComboBox) -> None:
    _pick(r, window, 2)


@scene("qcolorcombobox", width=200)
def _(r: Recorder, window: QComboBox) -> None:
    _pick(r, window, 2)


@scene("qcolormap", width=220)
def _(r: Recorder, window: QComboBox) -> None:
    _pick(r, window, 2)


spec("colormap_catalog", width=220)


# ---------------------------------------------------------------------------
# Home page


@scene("showcase", width=420)
def _(r: Recorder, window: QWidget) -> None:
    channel = window.findChild(QSearchableComboBox)
    limits = window.findChild(QLabeledRangeSlider)
    cmap = window.findChild(QColormapComboBox)
    switch = window.findChild(QToggleSwitch)

    _drag_handle(r, limits._slider, 0, 0.25)
    _pick(r, cmap, 1)
    cmap.setCurrentIndex(1)
    r.click(switch, QPoint(14, switch.height() // 2))
    r.wait(0.3)
    edit = channel.lineEdit()
    r.click(edit)
    edit.selectAll()
    r.leave(duration=0.3)
    r.type(edit, "ch")
    r.wait(0.6)
    _complete(r, channel)
    r.wait(1.0)
    # back to the start, for the next loop
    for widget in (channel, cmap):
        widget.setCurrentIndex(0)
    limits.setValue((30, 200))
    switch.setChecked(False)
    channel.completer().popup().hide()
    edit.clearFocus()
    r.wait(0.1)


# ---------------------------------------------------------------------------
# Stills

spec("qlargeintspinbox", width=180)
spec("qquantity", width=220)
spec("code_syntax_highlight", width=460, height=260)
