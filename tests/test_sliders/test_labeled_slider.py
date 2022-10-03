from unittest.mock import Mock

from superqt import QLabeledRangeSlider, QLabeledSlider


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


def _assert_types(args, type_):
    # sourcery skip: comprehension-to-generator
    assert all([isinstance(v, type_) for v in args]), "invalid type"


def test_labeled_signals(qtbot):  # sourcery skip: comprehension-to-generator
    ls = QLabeledSlider()
    qtbot.addWidget(ls)

    mock = Mock()
    ls.valueChanged.connect(mock)
    with qtbot.waitSignal(ls.valueChanged):
        ls.setValue(10)
    mock.assert_called_once_with(10)
    assert all([isinstance(v, int) for v in mock.call_args.args]), "invalid type"

    mock = Mock()
    ls.rangeChanged.connect(mock)
    with qtbot.waitSignal(ls.rangeChanged):
        ls.setMinimum(3)
    mock.assert_called_once_with(3, 99)
    _assert_types(mock.call_args.args, int)

    mock.reset_mock()
    with qtbot.waitSignal(ls.rangeChanged):
        ls.setMaximum(15)
    mock.assert_called_once_with(3, 15)
    _assert_types(mock.call_args.args, int)

    mock.reset_mock()
    with qtbot.waitSignal(ls.rangeChanged):
        ls.setRange(1, 2)
    mock.assert_called_once_with(1, 2)
    _assert_types(mock.call_args.args, int)
