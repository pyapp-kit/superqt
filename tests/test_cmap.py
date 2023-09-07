import numpy as np
import pytest

try:
    from cmap import Colormap
except ImportError:
    pytest.skip("cmap not installed", allow_module_level=True)

from qtpy.QtCore import QRect
from qtpy.QtGui import QPainter, QPixmap
from qtpy.QtWidgets import QStyleOptionViewItem, QWidget

from superqt.cmap import (
    CmapCatalogComboBox,
    QColormapItemDelegate,
    QColormapLineEdit,
    draw_colormap,
)
from superqt.utils import qimage_to_array


def test_draw_cmap(qtbot):
    # draw into a QWidget
    wdg = QWidget()
    qtbot.addWidget(wdg)
    draw_colormap(wdg, "viridis")
    # draw into any QPaintDevice
    draw_colormap(QPixmap(), "viridis")
    # pass a painter an explicit colormap and a rect
    draw_colormap(QPainter(), Colormap(("red", "yellow", "blue")), QRect())
    # test with a border
    draw_colormap(wdg, "viridis", border_color="red", border_width=2)

    with pytest.raises(TypeError, match="Expected a QPainter or QPaintDevice instance"):
        draw_colormap(QRect(), "viridis")  # type: ignore

    with pytest.raises(TypeError, match="Expected a Colormap instance or something"):
        draw_colormap(QPainter(), "not a recognized string or cmap", QRect())


def test_cmap_draw_result():
    """Test that the image drawn actually looks correct."""
    # draw into any QPaintDevice
    w = 100
    h = 20
    pix = QPixmap(w, h)
    cmap = Colormap("viridis")
    draw_colormap(pix, cmap)

    ary1 = cmap(np.tile(np.linspace(0, 1, w), (h, 1)), bytes=True)
    ary2 = qimage_to_array(pix.toImage())

    # there are some subtle differences between how qimage draws and how
    # cmap draws, so we can't assert that the arrays are exactly equal.
    # they are visually indistinguishable, and numbers are close within 4 (/255) values
    np.testing.assert_allclose(ary1, ary2, atol=4)


def test_catalog_combo(qtbot):
    wdg = CmapCatalogComboBox()
    qtbot.addWidget(wdg)
    wdg.show()

    wdg.setCurrentText("viridis")
    assert wdg.currentColormap() == Colormap("viridis")


def test_cmap_item_delegate(qtbot):
    wdg = CmapCatalogComboBox()
    qtbot.addWidget(wdg)
    view = wdg.view()
    delegate = view.itemDelegate()
    assert isinstance(delegate, QColormapItemDelegate)

    # smoke tests:
    painter = QPainter()
    option = QStyleOptionViewItem()
    index = wdg.model().index(0, 0)
    delegate._colormap_fraction = 1
    delegate.paint(painter, option, index)
    delegate._colormap_fraction = 0.33
    delegate.paint(painter, option, index)

    assert delegate.sizeHint(option, index) == delegate._item_size


def test_cmap_line_edit(qtbot, qapp):
    wdg = QColormapLineEdit()
    qtbot.addWidget(wdg)
    wdg.show()

    wdg.setColormap("viridis")
    assert wdg.colormap() == Colormap("viridis")
    wdg.setText("magma")  # also works if the name is recognized
    assert wdg.colormap() == Colormap("magma")
    qapp.processEvents()
    qtbot.wait(10)  # force the paintEvent

    wdg.setFractionalColormapWidth(1)
    wdg.update()
    qapp.processEvents()
    qtbot.wait(10)  # force the paintEvent

    wdg.setText("not-a-cmap")
    assert wdg.colormap() is None
    # or
    wdg.setColormap(None)
    assert wdg.colormap() is None
    qapp.processEvents()
    qtbot.wait(10)  # force the paintEvent
