from collections.abc import Iterable
from typing import Any
from unittest.mock import Mock

import pytest

from superqt import (
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QLabeledSlider,
)


def test_labeled_slider_api(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.hideBar()
    slider.showBar()
    slider.setBarVisible()
    slider.setBarMovesAllHandles()
    slider.setBarIsRigid()


def test_slider_connect_works(qtbot):
    slider = QLabeledSlider()
    qtbot.addWidget(slider)

    slider._label.editingFinished.emit()


def _assert_types(args: Iterable[Any], type_: type):
    # sourcery skip: comprehension-to-generator
    assert all(isinstance(v, type_) for v in args), "invalid type"


@pytest.mark.parametrize("cls", [QLabeledDoubleSlider, QLabeledSlider])
def test_labeled_signals(cls, qtbot):
    gslider = cls()
    qtbot.addWidget(gslider)

    type_ = float if cls == QLabeledDoubleSlider else int

    mock = Mock()
    gslider.valueChanged.connect(mock)
    with qtbot.waitSignal(gslider.valueChanged):
        gslider.setValue(10)
    mock.assert_called_once_with(10)
    _assert_types(mock.call_args.args, type_)

    mock = Mock()
    gslider.rangeChanged.connect(mock)
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setMinimum(3)
    mock.assert_called_once_with(3, 99)
    _assert_types(mock.call_args.args, type_)

    mock.reset_mock()
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setMaximum(15)
    mock.assert_called_once_with(3, 15)
    _assert_types(mock.call_args.args, type_)

    mock.reset_mock()
    with qtbot.waitSignal(gslider.rangeChanged):
        gslider.setRange(1, 2)
    mock.assert_called_once_with(1, 2)
    _assert_types(mock.call_args.args, type_)


@pytest.mark.parametrize(
    "cls", [QLabeledDoubleSlider, QLabeledRangeSlider, QLabeledSlider]
)
def test_editing_finished_signal(cls, qtbot):
    mock = Mock()
    slider = cls()
    qtbot.addWidget(slider)
    slider.editingFinished.connect(mock)
    if hasattr(slider, "_label"):
        slider._label.editingFinished.emit()
    else:
        slider._min_label.editingFinished.emit()
    mock.assert_called_once()


def test_editing_float(qtbot):
    slider = QLabeledDoubleSlider()
    qtbot.addWidget(slider)
    slider._label.setValue(0.5)
    slider._label.editingFinished.emit()
    assert slider.value() == 0.5


def test_slider_label_value(qtbot):
    slider = QLabeledDoubleSlider()
    qtbot.addWidget(slider)

    slider.setRange(-180, 180)
    assert slider._label._min == -180
    assert slider._label._max == 180

    slider.setValue(150)
    assert slider.value() == 150 == slider._label.value()

    slider.setValue(-90)
    assert slider.value() == -90 == slider._label.value()


def test_range_slider_handle_label_editing(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.show()
    assert slider.value() == (20, 80)

    # simulate editing the second handle label to 50
    slider._handle_labels[1].setValue(50)
    slider._handle_labels[1].editingFinished.emit()
    assert slider.value() == (20, 50)

    # simulate editing the first handle label to 10
    slider._handle_labels[0].setValue(10)
    slider._handle_labels[0].editingFinished.emit()
    assert slider.value() == (10, 50)


def test_range_slider_handle_label_resyncs_when_blocked(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.setRange(0, 100)
    slider.setValue((20, 50, 80))
    label = slider._handle_labels[1]

    # the middle handle can't pass the upper handle, so typing 500 twice
    # leaves the value unchanged on the second edit
    for _ in range(2):
        label.setText("500")
        label.editingFinished.emit()
        assert slider.value() == (20, 79, 80)
        assert label.value() == 79
        assert label.text() == "79"


def _type_into(label, text: str) -> None:
    label.setText(text)
    label.editingFinished.emit()


@pytest.mark.parametrize("cls", [QLabeledRangeSlider, QLabeledDoubleRangeSlider])
def test_expand_range_on_handle_edit(cls, qtbot):
    slider = cls()
    qtbot.addWidget(slider)
    slider.setRange(0, 100)
    slider.setValue((20, 80))
    lo, hi = slider._handle_labels

    # off by default: typed values are clamped
    assert not slider.expandRangeOnHandleEdit()
    with qtbot.waitSignal(hi.valueEdited) as blocker:
        _type_into(hi, "150")
    assert blocker.args == [100.0]
    _type_into(lo, "-50")
    assert (slider.minimum(), slider.maximum()) == (0, 100)

    slider.setExpandRangeOnHandleEdit(True)
    _type_into(hi, "150")
    _type_into(lo, "-50")
    assert (slider.minimum(), slider.maximum()) == (-50, 150)
    assert slider.value() == (-50, 150)

    # range only grows on the side a handle can actually move toward
    _type_into(lo, "500")
    _type_into(hi, "-500")
    assert (slider.minimum(), slider.maximum()) == (-50, 150)
    assert [lo.value(), hi.value()] == list(slider.value())

    slider.setExpandRangeOnHandleEdit(False)
    _type_into(hi, "500")
    assert slider.maximum() == 150


def test_expand_range_on_handle_edit_middle_handle(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.setRange(0, 100)
    slider.setExpandRangeOnHandleEdit(True)
    slider.setValue((20, 50, 80))  # recreates handle labels

    _type_into(slider._handle_labels[1], "500")
    assert slider.maximum() == 100
    _type_into(slider._handle_labels[2], "500")
    assert slider.maximum() == 500


def test_slider_label_decimals_update_text(qtbot):
    slider = QLabeledDoubleSlider()
    qtbot.addWidget(slider)

    # Set a value with default 2 decimals
    slider.setValue(3.14159)
    assert slider.value() == 3.14159
    assert slider._label.text() == "3.14"

    slider.setDecimals(0)
    assert slider._label.text() == "3"

    slider.setDecimals(4)
    assert slider._label.text() == "3.1416"


def test_qlabeled_range_slider_large_range_does_not_typeerror(qtbot):
    """Regression for examples/labeled_sliders.py on Windows/PyQt6 (#308)."""
    sld = QLabeledRangeSlider()
    qtbot.addWidget(sld)
    big = 10**11
    # setRange should not raise TypeError from rangeChanged.emit
    sld.setRange(0, big)
    assert sld.minimum() == 0
    assert sld.maximum() == big
    # example also sets a large value tuple
    sld.setValue((20, 60 * 10**9))
    v = sld.value()
    assert v[0] == 20
    assert v[1] == 60 * 10**9
