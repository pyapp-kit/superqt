from cmap import Colormap
from qtpy.QtWidgets import QApplication

from superqt import QColormapComboBox

app = QApplication([])

# (allow_user_colormaps adds an "Add Colormap..." item, to choose from the catalog)
cmap_combo = QColormapComboBox(allow_user_colormaps=True)
# see note above about colormap-like objects
# as names from the cmap catalog
cmap_combo.addColormaps(["viridis", "plasma", "magma", "gray"])
# as a sequence of colors, linearly interpolated
cmap_combo.addColormap(("#0f0", "slateblue", "#F3A003A0"))
# as a `cmap.Colormap` instance with custom name:
cmap_combo.addColormap(Colormap(("green", "white", "orange"), name="MyMap"))

cmap_combo.show()
app.exec()
