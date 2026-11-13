"""How each docs example is captured, and the animations recorded for some.

Examples without an entry here are captured as shown, without animation. A scene
receives a `Recorder` (see `_media.py`) and the window that the example shows;
`r.wait(...)` holds still, everything else moves the cursor or types.
Scenes should end where they start, so the animation loops smoothly.
"""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING

from _media import FPS, scene, spec
from qtpy.QtCore import QPoint, Qt
from qtpy.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QSlider,
    QStyle,
    QStyleOptionSlider,
)

from superqt import (
    QColormapComboBox,
    QLabeledRangeSlider,
    QSearchableComboBox,
    QToggleSwitch,
)
from superqt.fonticon import Animation
from superqt.utils import signals_blocked

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


def _edit_label(r: Recorder, label: QWidget, text: str) -> None:
    """Type a value into a slider's label (a line edit), and press Enter."""
    r.click(label)
    label.selectAll()
    r.leave(duration=0.3)
    r.type(label, text)
    r.wait(0.3)
    r.key(label, Qt.Key.Key_Return)
    r.wait(0.8)


def _labeled_single_scene(r: Recorder, window: QWidget) -> None:
    # drag the handle, then type the value it started at into the label
    initial = window.value()
    _drag_handle(r, window._slider, 0, 0.3)
    _edit_label(r, window._label, f"{initial:g}")


def _labeled_range_scene(r: Recorder, window: QWidget) -> None:
    # drag a handle and the bar, then type the upper handle's start value in its label
    initial = window.value()
    slider = window._slider
    _drag_handle(r, slider, 0, 0.25)
    bar = (_handle(slider, 0) + _handle(slider, 1)) / 2
    r.drag(slider, bar, bar - QPoint(round(slider.width() * 0.25), 0), duration=0.8)
    r.wait(0.3)
    _edit_label(r, window._handle_labels[-1], f"{initial[-1]:g}")
    window.setValue(initial)  # (in case the drags rounded the lower value)


# (narrow enough that the gallery cards don't shrink them much)
SLIDER = {"width": 360}
for name in ("qrangeslider", "qdoublerangeslider"):
    spec(name, scene=_range_scene, **SLIDER)
spec("qdoubleslider", scene=_single_scene, **SLIDER)
for name in ("qlabeledrangeslider", "qlabeleddoublerangeslider"):
    spec(name, scene=_labeled_range_scene, **SLIDER)
for name in ("qlabeledslider", "qlabeleddoubleslider"):
    spec(name, scene=_labeled_single_scene, **SLIDER)


# ---------------------------------------------------------------------------
# Buttons, containers and layouts


@scene("qtoggleswitch", width=170)
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


@scene("qelidinglineedit", width=300)
def _(r: Recorder, window: QWidget) -> None:
    r.click(window, QPoint(150, window.height() // 2))
    r.key(window, Qt.Key.Key_End)
    r.leave(duration=0.3)
    r.wait(1.2)
    window.clearFocus()
    r.wait(0.3)


@scene("fonticon_animation", seamless=True)
def _(r: Recorder, window: QWidget) -> None:
    # Step the animations by frame number, not by their timers, for 14.4 s: a whole
    # number of turns of both (spin: 1° per 10 ms; pulse: 45° per 200 ms), so the
    # loop is seamless.
    animations = [obj for obj in gc.get_objects() if isinstance(obj, Animation)]
    rates = [(anim._step, anim.timer.interval()) for anim in animations]
    for anim in animations:
        anim.timer.setInterval(
            2**31 - 1
        )  # (still active, so `animate` won't restart it)
    for i in range(round(14.4 * FPS)):
        for anim, (step, interval) in zip(animations, rates, strict=True):
            anim._angle = step * (i * 1000 // (FPS * interval))
            anim.parent_widget.update()
        r.frame()


@scene("qcolormaplineedit", width=260)
def _(r: Recorder, window: QWidget) -> None:
    # the swatch follows the text: the fallback until the name is a colormap
    r.click(window)
    window.selectAll()
    r.leave(duration=0.3)
    r.type(window, "magma", interval=0.15)
    r.wait(1.0)
    window.selectAll()
    r.type(window, "viridis", interval=0.15)
    r.wait(0.4)
    window.clearFocus()


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


@scene("qsearchabletreewidget", width=320, height=380)
def _(r: Recorder, window: QWidget) -> None:
    r.click(window.filter)
    r.leave(duration=0.3)
    r.type(window.filter, "fl")
    r.wait(0.9)
    r.key(window.filter, Qt.Key.Key_Backspace, times=2)


@scene("qsearchablecombobox", width=200)
def _(r: Recorder, window: QComboBox) -> None:
    _search(r, window, "baz")
    r.wait(1.0)
    window.setCurrentIndex(0)
    window.lineEdit().clearFocus()


@scene("colormap_catalog", width=220)
def _(r: Recorder, window: QComboBox) -> None:
    _search(r, window, "ice")
    r.wait(1.0)
    window.setCurrentText("viridis")
    window.lineEdit().clearFocus()


def _search(r: Recorder, combo: QComboBox, text: str) -> None:
    """Type into an editable combo box, and pick the first completion."""
    edit = combo.lineEdit()
    r.click(edit)
    edit.selectAll()
    r.leave(duration=0.3)
    r.type(edit, text)
    r.wait(0.6)
    popup = combo.completer().popup()
    r.key(popup, Qt.Key.Key_Down, interval=0.3)
    r.key(popup, Qt.Key.Key_Return)


# ---------------------------------------------------------------------------
# Combo boxes: open the popup and pick an item


def _pick(r: Recorder, combo: QComboBox, index: int, restore: bool = True) -> None:
    initial = combo.currentIndex()
    r.click(combo)
    r.wait(0.3)
    view = combo.view()
    r.move(view, view.visualRect(combo.model().index(index, 0)).center())
    r.wait(0.3)
    r.press()
    r.release()
    r.wait(0.8)
    if restore:
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

    # then add one from the catalog, with "Add Colormap..." (a dialog)
    def in_dialog(dialog: QWidget) -> None:
        _search(r, dialog.combo, "ice")
        r.wait(0.6)
        buttons = dialog.findChild(QDialogButtonBox)
        r.move(buttons.button(QDialogButtonBox.StandardButton.Ok))
        r.press()
        r.release(wait=0)  # (so that the dialog's `exec()` returns at once)

    r.click(window)
    r.wait(0.3)
    view = window.view()
    add = view.visualRect(window.model().index(window.count() - 1, 0))
    r.click_into_modal(view, add.center(), in_dialog)
    r.wait(1.2)
    r.leave()
    # back to the start, for the next loop
    window.removeItem(window.currentIndex())
    window.setCurrentIndex(0)


# ---------------------------------------------------------------------------
# Throttling


@scene("throttling", width=520)
def _(r: Recorder, window: QWidget) -> None:
    slider = window.findChild(QSlider)
    initial = slider.value()
    start = _handle(slider, 0)
    r.drag(slider, start, start + QPoint(round(slider.width() * 0.5), 0), duration=1.8)
    r.wait(1.0)
    here = _handle(slider, 0)
    r.drag(slider, here, start, duration=1.8)
    r.leave()
    with signals_blocked(slider):
        slider.setValue(initial)  # (in case the drags rounded it)
    r.wait(4.2)  # until the ticks have scrolled off, so the loop is seamless


# ---------------------------------------------------------------------------
# Icons


@scene("iconify_states")
def _(r: Recorder, window: QWidget) -> None:
    r.click(window)
    r.wait(1.0)
    r.click(window, duration=0.2)
    r.leave()


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
    _search(r, channel, "ch")
    r.wait(1.0)
    # back to the start, for the next loop
    for widget in (channel, cmap):
        widget.setCurrentIndex(0)
    limits.setValue((30, 200))
    switch.setChecked(False)
    channel.completer().popup().hide()
    channel.lineEdit().clearFocus()
    r.wait(0.1)


# ---------------------------------------------------------------------------
# Stills

spec("qlargeintspinbox", width=180)


@scene("qquantity", width=220)
def _(r: Recorder, window: QWidget) -> None:
    # changing the units converts the value: 1 m, 1000 mm, 0.001 km, 1 m
    combo = window.unitsComboBox()
    for unit in ("mm", "km", "m"):
        _pick(r, combo, combo.findText(unit), restore=False)
    r.leave()


spec("code_syntax_highlight", width=460, height=260)
