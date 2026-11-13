from qtpy.QtWidgets import QApplication

from superqt import QElidingLabel

app = QApplication([])

label = QElidingLabel(
    "This text is too long for the label, so the end of it is replaced with an "
    "ellipsis. Make the window wider to see more of it."
)
label.resize(300, 20)
label.show()

app.exec()
