from qtpy.QtWidgets import QApplication, QPushButton, QWidget

from superqt import QFlowLayout

app = QApplication([])

wdg = QWidget()

layout = QFlowLayout(wdg)
layout.addWidget(QPushButton("Short"))
layout.addWidget(QPushButton("Longer"))
layout.addWidget(QPushButton("Different text"))
layout.addWidget(QPushButton("More text"))
layout.addWidget(QPushButton("Even longer button text"))

wdg.setWindowTitle("Flow Layout")
wdg.show()

app.exec()
