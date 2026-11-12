from qtpy.QtWidgets import QApplication

from superqt import QElidingLineEdit

app = QApplication([])

line_edit = QElidingLineEdit(
    "/Users/me/Documents/projects/experiments/2026-11-12/results/summary.csv"
)
line_edit.resize(300, 30)
line_edit.show()

app.exec()
