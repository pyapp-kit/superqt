from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from qtpy import QT_VERSION

from superqt import QDoubleSlider, QLabeledRangeSlider, QRangeSlider

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.mark.skipif(QT_VERSION.startswith("5"), reason="the patch is for Qt 5")
@pytest.mark.parametrize("cls", [QDoubleSlider, QRangeSlider, QLabeledRangeSlider])
def test_mac_style_patch_does_nothing_with_qt6(qtbot: QtBot, cls: type) -> None:
    slider = cls()
    qtbot.addWidget(slider)
    style_sheet = slider.styleSheet()
    with pytest.warns(DeprecationWarning, match="does nothing with Qt 6"):
        slider.applyMacStylePatch()
    assert slider.styleSheet() == style_sheet
