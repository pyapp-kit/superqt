from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

btn = QPushButton()

# search https://icon-sets.iconify.design for available icon keys
btn.setIcon(QIconifyIcon("fa:smile-o", color="blue"))
btn.setIconSize(QSize(60, 60))
btn.show()

app.exec()
