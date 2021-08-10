from superqt.fonticon import icon
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

btn = QPushButton()
btn.setIcon(icon("lnr.cloud"))
btn.setIconSize(QSize(512, 512))
btn.show()

# btn2 = QPushButton()
# btn2.setIcon(icon("mdi5.loading", animation=spin(btn2)))
# btn2.setIconSize(QSize(225, 225))
# btn2.show()

# btn3 = QPushButton()
# setTextIcon(btn3, FA5Solid.air_freshener, size=256)
# btn3.show()


app.exec()
