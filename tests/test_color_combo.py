from qtpy.QtGui import QColor

from superqt import QColorComboBox


def test_QColorComboBox(qtbot):
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

    wdg.clear()
    assert wdg.count() == 1  # "Add Color" item
    wdg.setUserColorsAllowed(False)
    assert not wdg.count()
