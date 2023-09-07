import sys

from cmap import Colormap
from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

from superqt import QColormapComboBox
from superqt.combobox._colormap_combobox import CmapCatalogComboBox

app = QApplication([])

wdg = QWidget()
layout = QVBoxLayout(wdg)
w2 = CmapCatalogComboBox()
layout.addWidget(w2)
wdg.show()
app.exec()
sys.exit()

w = QColormapComboBox()
# adds an item "Add Color" that opens a QColorDialog when clicked
w.setUserColorsAllowed(True)

# any colormap-like object:
# https://cmap-docs.readthedocs.io/en/latest/colormaps/#colormaplike-objects

# colors can be any argument that can be passed to QColor
# (tuples and lists will be expanded to QColor(*color)
COLORMAPS = [
    "viridis",
    "inferno",
    "magma",
    "accent",
    ("blue", "yellow", "red"),
    Colormap(
        {"red": lambda x: x, "green": lambda x: x**2, "blue": lambda x: x**0.5},
        name="MyColormap",
    ),
]
w.addColormaps(COLORMAPS)


# as with addColors, colors will be cast to QColor when using setColors
w.setCurrentColormap("indigo")

w.resize(200, 50)
w.show()

w.currentColorChanged.connect(print)
app.exec_()
