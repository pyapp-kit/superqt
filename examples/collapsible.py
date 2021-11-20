"""Example for QCollapsible"""
from PySide2.QtWidgets import QLabel
from superqt import QCollapsible
from superqt.qtcompat.QtWidgets import QApplication, QPushButton, QLabel

app = QApplication([])

collapsible = QCollapsible("Advanced analysis")
collapsible.addWidget(QLabel("This is the inside of the collapsible frame"))
for i in range(10):
    collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

collapsible.expand(animate=False)
collapsible.show()
app.exec_()
