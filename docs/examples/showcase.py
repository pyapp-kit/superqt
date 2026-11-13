from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication, QFormLayout, QWidget

from superqt import (
    QColormapComboBox,
    QLabeledDoubleSlider,
    QLabeledRangeSlider,
    QSearchableComboBox,
    QToggleSwitch,
)

app = QApplication([])

panel = QWidget()
form = QFormLayout(panel)
form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

channel = QSearchableComboBox()
channel.addItems(["DAPI", "GFP", "mCherry", "Cy5", "Brightfield"])
form.addRow("Channel", channel)

limits = QLabeledRangeSlider(Qt.Orientation.Horizontal)
limits.setRange(0, 255)
limits.setValue((30, 200))
form.addRow("Contrast", limits)

cmap = QColormapComboBox()
cmap.addColormaps(["viridis", "magma", "inferno", "gray"])
form.addRow("Colormap", cmap)

form.addRow("Auto-scale", QToggleSwitch())

gamma = QLabeledDoubleSlider(Qt.Orientation.Horizontal)
gamma.setRange(0.1, 3)
gamma.setValue(1)
form.addRow("Gamma", gamma)

panel.show()
app.exec()
