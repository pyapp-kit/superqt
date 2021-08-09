from superqt.fonticon import icon
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

# btn = QPushButton()
# btn.setIcon(icon(FA5Brands.app_store))
# btn.setIconSize(QSize(512, 512))
# btn.show()

btn2 = QPushButton()
btn2.setIcon(icon("mdi5.ab-testing"))
btn2.setIconSize(QSize(512, 512))
btn2.show()

app.exec()
