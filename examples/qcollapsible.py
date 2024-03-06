"""Example for QCollapsible."""

from qtpy.QtWidgets import QApplication, QLabel, QPushButton

from superqt import QCollapsible

app = QApplication([])

collapsible = QCollapsible("Advanced analysis")
collapsible.setCollapsedIcon("+")
collapsible.setExpandedIcon("-")
collapsible.addWidget(QLabel("This is the inside of the collapsible frame"))
for i in range(10):
    collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

collapsible.expand(animate=False)
collapsible.show()
app.exec_()
