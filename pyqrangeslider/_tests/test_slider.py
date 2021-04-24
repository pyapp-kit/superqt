import pytest

from pyqrangeslider import QRangeSlider
from pyqrangeslider.qtcompat.QtCore import Qt


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_basic(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)
