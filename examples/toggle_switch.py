from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

from superqt import QToggleSwitch


class QRectangleToggleSwitch(QToggleSwitch):
    """A rectangle shaped toggle switch."""

    def drawGroove(self, painter, rect, option) -> None:
        """Draw the groove of the switch."""
        painter.drawRect(rect)

    def drawHandle(self, painter, rect, option):
        """Draw the handle of the switch."""
        painter.drawRect(rect)


class QToggleSwitchWithText(QToggleSwitch):
    """A toggle switch with text on the handle."""

    def drawHandle(self, painter, rect, option):
        super().drawHandle(painter, rect, option)
        if self.isChecked():
            text = "ON"
        else:
            text = "OFF"
        painter.setPen(QtGui.QPen(QtGui.QColor("black")))
        font = painter.font()
        font.setPointSize(5)
        painter.setFont(font)
        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)


app = QApplication([])
widget = QWidget()
layout = QVBoxLayout(widget)
layout.addWidget(QToggleSwitch("original"))
layout.addWidget(QRectangleToggleSwitch("rectangle"))
layout.addWidget(QToggleSwitchWithText("with text"))
widget.show()
app.exec_()
