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
    assert all([isinstance(v, type_) for v in args]), "invalid type"


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
