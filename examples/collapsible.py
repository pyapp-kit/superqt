"""Example for QCollapsible"""
from PySide2.QtWidgets import QLabel
from qtpy.QtWidgets import QApplication, QLabel, QPushButton

from superqt import QCollapsible

app = QApplication([])

collapsible = QCollapsible("Advanced analysis")
collapsible.addWidget(QLabel("This is the inside of the collapsible frame"))
for i in range(10):
    collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

collapsible.expand(animate=False)
collapsible.show()
app.exec_()
