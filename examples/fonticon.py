from superqt.fonticon import icon, setTextIcon, spin
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

btn = QPushButton()
btn.setIcon(icon("fthr4.activity"))
btn.setIconSize(QSize(256, 256))
btn.show()

btn2 = QPushButton()
btn2.setIcon(icon("fa5s.spinner", animation=spin(btn2)))
btn2.setIconSize(QSize(225, 225))
btn2.show()

btn3 = QPushButton()
btn3.resize(275, 275)
setTextIcon(btn3, "fthr4.activity")
btn3.show()


app.exec()
