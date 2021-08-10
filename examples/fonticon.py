from superqt.fonticon import icon, step
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

# btn = QPushButton()
# btn.setIcon(icon(FA5Brands.app_store))
# btn.setIconSize(QSize(512, 512))
# btn.show()

btn2 = QPushButton()
btn2.setIcon(icon("fa5s.spinner", animation=step(btn2)))
btn2.setIconSize(QSize(225, 225))
btn2.show()

app.exec()
