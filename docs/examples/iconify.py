from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

btn = QPushButton()
btn.setIcon(QIconifyIcon("fluent-emoji-flat:alarm-clock"))
btn.setIconSize(QSize(60, 60))
btn.show()

app.exec()
