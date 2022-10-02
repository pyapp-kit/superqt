from qtpy import QtCore
from qtpy import QtWidgets as QtW

app = QtW.QApplication([])

QSS = """
QSlider::groove {
    background: #DFDFDF;
    border: 1px solid #DBDBDB;
    border-radius: 2px;
}
QSlider::groove:horizontal {
    height: 2px;
    margin: 2px;
}
QSlider::groove:vertical {
    width: 2px;
    margin: 2px 0 6px 0;
}


QSlider::handle {
    background: white;
    border: 0.5px solid #DADADA;
    width: 19.5px;
    height: 19.5px;
    border-radius: 10.5px;
}
QSlider::handle:horizontal {
    margin: -10px -2px;
}
QSlider::handle:vertical {
    margin: -2px -10px;
}

QSlider::handle:pressed {
    background: #F0F0F0;
}


QSlider::sub-page:horizontal {
    background: #0981FE;
    border: 1px solid #097DF7;
    border-radius: 2px;
    margin: 2px;
    height: 2px;
}
QSlider::add-page:vertical {
    background: #0981FE;
    border: 1px solid #097DF7;
    border-radius: 2px;
    margin: 2px 0 6px 0;
    width: 2px;
}
"""

L = QtCore.Qt.Orientation.Vertical

w = QtW.QWidget()
w.setLayout(QtW.QHBoxLayout() if int(L) == 2 else QtW.QVBoxLayout())
s1 = QtW.QSlider(L)
s1.setStyleSheet(QSS)
s2 = QtW.QSlider(L)
w.layout().addWidget(s1)
w.layout().addWidget(s2)
w.show()
app.exec_()
