from superqt.fonticon import MI4Round, icon
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])
btn = QPushButton()
btn.setIcon(icon(MI4Round.gpp_good))
btn.setIconSize(QSize(512, 512))
btn.show()

app.exec()
