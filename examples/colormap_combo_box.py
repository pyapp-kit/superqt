from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

from superqt.cmap import CmapCatalogComboBox, QColormapComboBox

app = QApplication([])

wdg = QWidget()
layout = QVBoxLayout(wdg)

catalog_combo = CmapCatalogComboBox(interpolation="linear")

selected_cmap_combo = QColormapComboBox(allow_user_colormaps=True)
selected_cmap_combo.addColormaps(["viridis", "plasma", "magma", "inferno", "turbo"])

layout.addWidget(catalog_combo)
layout.addWidget(selected_cmap_combo)

wdg.show()
app.exec()
