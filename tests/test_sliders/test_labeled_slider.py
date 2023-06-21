import sys
from typing import Any, Iterable
from unittest.mock import Mock

import pytest

from superqt import QLabeledDoubleSlider, QLabeledRangeSlider, QLabeledSlider


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
    if sys.version_info >= (3, 8):
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


@pytest.mark.parametrize("cls", [QLabeledSlider, QLabeledDoubleSlider])
def test_extended_label_spinbox_range(cls, qtbot):
    slider = cls()
    mock = Mock()
    qtbot.addWidget(slider)
    slider.setRange(0, 10)
    slider.rangeChanged.connect(mock)
    assert slider._label.minimum() == 0
    assert slider._label.maximum() == 10
    assert slider.minimum() == 0
    assert slider.maximum() == 10

    # changing slider value without changing spinbox range should return a clipped value
    # slider._label.setValue(20)
    # slider._label.editingFinished.emit()  # simulate editing the label manually
    # qtbot.wait(20)
    # assert slider.value() == 10
    # assert slider.maximum() == 10

    # after changing label range, setting the label to a value outside the range should
    # update the slider min/max as appropriate
    slider.setLabelSpinBoxRange(-10, 20)

    with qtbot.waitSignal(slider.rangeChanged):
        slider._label.setValue(15)
        assert slider._label.minimum() == -10
        slider._label.editingFinished.emit()  # simulate editing the label manually
        assert slider._label.minimum() == -10
    assert slider.value() == 15
    assert slider.minimum() == 0  # unchanged
    assert slider.maximum() == 15  # changed

    with qtbot.waitSignal(slider.rangeChanged):
        slider._label.setValue(-5)
        slider._label.editingFinished.emit()  # simulate editing the label manually
    assert slider.value() == -5
    assert slider.minimum() == -5  # changed
    assert slider.maximum() == 15  # unchanged
