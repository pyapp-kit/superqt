import pytest

from qtrangeslider import QRangeSlider
from qtrangeslider.qtcompat.QtCore import Qt


@pytest.mark.parametrize("orientation", ["Horizontal", "Vertical"])
def test_basic(qtbot, orientation):
    rs = QRangeSlider(getattr(Qt, orientation))
    qtbot.addWidget(rs)
