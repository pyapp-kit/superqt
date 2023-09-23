from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication

from superqt import QColorComboBox

app = QApplication([])
w = QColorComboBox()
# adds an item "Add Color" that opens a QColorDialog when clicked
w.setUserColorsAllowed(True)

# colors can be any argument that can be passed to QColor
# (tuples and lists will be expanded to QColor(*color)
COLORS = [QColor("red"), "orange", (255, 255, 0), "green", "#00F", "indigo", "violet"]
w.addColors(COLORS)

# as with addColors, colors will be cast to QColor when using setColors
w.setCurrentColor("indigo")

w.resize(200, 50)
w.show()

w.currentColorChanged.connect(print)
app.exec_()
