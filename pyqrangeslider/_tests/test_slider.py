import pytest
from qtpy.QtCore import Qt

from pyqrangeslider import QRangeSlider


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_basic(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)
