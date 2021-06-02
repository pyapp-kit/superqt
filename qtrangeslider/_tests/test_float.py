import os

import pytest

from qtrangeslider import (
    QDoubleRangeSlider,
    QDoubleSlider,
    QLabeledDoubleRangeSlider,
    QLabeledDoubleSlider,
)
from qtrangeslider.qtcompat import API_NAME

range_types = {QDoubleRangeSlider, QLabeledDoubleRangeSlider}


@pytest.fixture(
    params=[
        QDoubleSlider,
        QLabeledDoubleSlider,
        QDoubleRangeSlider,
        QLabeledDoubleRangeSlider,
    ]
)
def ds(qtbot, request):
    # convenience fixture that converts value() and setValue()
    # to let us use setValue((a, b)) for both range and non-range sliders
    cls = request.param
    wdg = cls()
    qtbot.addWidget(wdg)

    def assert_val_type():
        type_ = float
        if cls in range_types:
            assert all([isinstance(i, type_) for i in wdg.value()])  # sourcery skip
        else:
            assert isinstance(wdg.value(), type_)

    def assert_val_eq(val):
        assert wdg.value() == val if cls is QDoubleRangeSlider else val[0]

    wdg.assert_val_type = assert_val_type
    wdg.assert_val_eq = assert_val_eq

    if cls not in range_types:
        superset = wdg.setValue

        def _safe_set(val):
            superset(val[0] if isinstance(val, tuple) else val)

        wdg.setValue = _safe_set

    return wdg


def test_double_sliders(ds):
    ds.setMinimum(10)
    ds.setMaximum(99)
    ds.setValue((20, 40))
    ds.setSingleStep(1)
    assert ds.minimum() == 10
    assert ds.maximum() == 99
    ds.assert_val_eq((20, 40))
    assert ds.singleStep() == 1

    ds.assert_val_eq((20, 40))
    ds.assert_val_type()

    ds.setValue((20.23, 40.23))
    ds.assert_val_eq((20.23, 40.23))
    ds.assert_val_type()

    assert ds.minimum() == 10
    assert ds.maximum() == 99
    assert ds.singleStep() == 1
    ds.assert_val_eq((20.23, 40.23))
    ds.setValue((20.2343, 40.2342))
    ds.assert_val_eq((20.2343, 40.2342))

    ds.assert_val_eq((20.2343, 40.2342))
    assert ds.minimum() == 10
    assert ds.maximum() == 99
    assert ds.singleStep() == 1

    ds.assert_val_eq((20.2343, 40.2342))
    assert ds.minimum() == 10
    assert ds.maximum() == 99
    assert ds.singleStep() == 1


def test_double_sliders_small(ds):
    ds.setMaximum(1)
    ds.setValue((0.5, 0.9))
    assert ds.minimum() == 0
    assert ds.maximum() == 1
    ds.assert_val_eq((0.5, 0.9))

    ds.setValue((0.122233, 0.72644353))
    ds.assert_val_eq((0.122233, 0.72644353))


def test_double_sliders_big(ds):
    ds.setValue((20, 80))
    ds.setMaximum(5e14)
    assert ds.minimum() == 0
    assert ds.maximum() == 5e14
    ds.setValue((1.74e9, 1.432e10))
    ds.assert_val_eq((1.74e9, 1.432e10))


@pytest.mark.skipif(
    os.name == "nt" and API_NAME == "PyQt6", reason="Not ready for pyqt6"
)
def test_signals(ds, qtbot):
    with qtbot.waitSignal(ds.valueChanged):
        ds.setValue((10, 20))

    with qtbot.waitSignal(ds.rangeChanged):
        ds.setMinimum(0.5)

    with qtbot.waitSignal(ds.rangeChanged):
        ds.setMaximum(3.7)

    with qtbot.waitSignal(ds.rangeChanged):
        ds.setRange(1.2, 3.3)
