from qtpy.QtWidgets import QApplication

from superqt.cmap import CmapCatalogComboBox

app = QApplication([])

catalog_combo = CmapCatalogComboBox(interpolation="linear")
catalog_combo.setCurrentText("viridis")
catalog_combo.show()

app.exec()
