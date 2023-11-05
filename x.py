"""Example for QCollapsible."""
from qtpy.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from superqt import QCollapsible

app = QApplication([])

main_widget = QWidget()
layout = QVBoxLayout()
main_widget.setLayout(layout)


collapsible_bad = QCollapsible("Advanced analysis")
collapsible_bad.setStyleSheet("background: red;")
table = QTableWidget(20, 2)
collapsible_bad.addWidget(table)
collapsible_bad.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
layout.addWidget(collapsible_bad)


collapsible = QCollapsible("Advanced analysis (not bad)")
collapsible.setStyleSheet("background: blue;")
collapsible.addWidget(QLabel("This is the inside of the collapsible frame"))
for i in range(3):
    collapsible.addWidget(QPushButton(f"Content button {i + 1}"))
layout.addWidget(collapsible)

layout.addStretch()
layout.setSpacing(0)
main_widget.show()

app.exec_()
