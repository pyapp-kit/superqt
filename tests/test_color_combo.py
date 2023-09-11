from unittest.mock import patch

import pytest
from qtpy import API_NAME
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QStyleOptionViewItem

from superqt import QColorComboBox
from superqt.combobox import _color_combobox


def test_q_color_combobox(qtbot):
    wdg = QColorComboBox()
    qtbot.addWidget(wdg)
    wdg.show()
    wdg.setUserColorsAllowed(True)

    # colors can be any argument that can be passed to QColor
    # (tuples and lists will be expanded to QColor(*color)
    COLORS = [QColor("red"), "orange", (255, 255, 0), "green", "#00F", "indigo"]
    wdg.addColors(COLORS)

    colors = [wdg.itemColor(i) for i in range(wdg.count())]
    assert colors == [
        QColor("red"),
        QColor("orange"),
        QColor("yellow"),
        QColor("green"),
        QColor("blue"),
        QColor("indigo"),
        None,  # "Add Color" item
    ]

    # as with addColors, colors will be cast to QColor when using setColors
    wdg.setCurrentColor("indigo")
    assert wdg.currentColor() == QColor("indigo")
    assert wdg.currentColorName() == "#4b0082"

    wdg.clear()
    assert wdg.count() == 1  # "Add Color" item
    wdg.setUserColorsAllowed(False)
    assert not wdg.count()

    wdg.setInvalidColorPolicy(wdg.InvalidColorPolicy.Ignore)
    wdg.setInvalidColorPolicy(2)
    wdg.setInvalidColorPolicy("Raise")
    with pytest.raises(TypeError):
        wdg.setInvalidColorPolicy(1.0)  # type: ignore

    with pytest.raises(ValueError):
        wdg.addColor("invalid")


def test_q_color_delegate(qtbot):
    wdg = QColorComboBox()
    view = wdg.view()
    delegate = wdg.itemDelegate()
    qtbot.addWidget(wdg)
    wdg.show()

    # smoke tests:
    painter = QPainter()
    option = QStyleOptionViewItem()
    index = wdg.model().index(0, 0)
    delegate.paint(painter, option, index)

    wdg.addColors(["red", "orange", "yellow"])
    view.selectAll()
    index = wdg.model().index(1, 0)
    delegate.paint(painter, option, index)


@pytest.mark.skipif(API_NAME == "PySide2", reason="hangs on CI")
def test_activated(qtbot):
    wdg = QColorComboBox()
    qtbot.addWidget(wdg)
    wdg.show()
    wdg.setUserColorsAllowed(True)

    with patch.object(_color_combobox.QColorDialog, "getColor", lambda: QColor("red")):
        wdg._on_activated(wdg.count() - 1)  # "Add Color" item
    assert wdg.currentColor() == QColor("red")

    with patch.object(_color_combobox.QColorDialog, "getColor", lambda: QColor()):
        wdg._on_activated(wdg.count() - 1)  # "Add Color" item
    assert wdg.currentColor() == QColor("red")
