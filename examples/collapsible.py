"""Example for QCollapsible"""
from superqt import QCollapsible
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

collapsible = QCollapsible("Advanced analysis")
for i in range(10):
    collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

collapsible.show()
app.exec_()
