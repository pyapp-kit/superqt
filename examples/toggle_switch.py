from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QApplication, QStyle, QVBoxLayout, QWidget

from superqt import QToggleSwitch
from superqt.switch import QStyleOptionToggleSwitch

QSS_EXAMPLE = """
QToggleSwitch {
    qproperty-onColor: red;
    qproperty-handleSize: 12;
    qproperty-switchWidth: 30;
    qproperty-switchHeight: 16;
}
"""


class QRectangleToggleSwitch(QToggleSwitch):
    """A rectangle shaped toggle switch."""

    def drawGroove(
        self,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        option: QStyleOptionToggleSwitch,
    ) -> None:
        """Draw the groove of the switch."""
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        is_checked = option.state & QStyle.StateFlag.State_On
        painter.setBrush(option.on_color if is_checked else option.off_color)
        painter.setOpacity(0.8)
        painter.drawRect(rect)

    def drawHandle(self, painter, rect, option):
        """Draw the handle of the switch."""
        painter.drawRect(rect)


class QToggleSwitchWithText(QToggleSwitch):
    """A toggle switch with text on the handle."""

    def drawHandle(
        self,
        painter: QtGui.QPainter,
        rect: QtCore.QRectF,
        option: QStyleOptionToggleSwitch,
    ) -> None:
        super().drawHandle(painter, rect, option)

        text = "ON" if option.state & QStyle.StateFlag.State_On else "OFF"
        painter.setPen(QtGui.QPen(QtGui.QColor("black")))
        font = painter.font()
        font.setPointSize(5)
        painter.setFont(font)
        painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignCenter, text)


app = QApplication([])
widget = QWidget()
layout = QVBoxLayout(widget)
layout.addWidget(QToggleSwitch("original"))
switch_styled = QToggleSwitch("stylesheet")
switch_styled.setStyleSheet(QSS_EXAMPLE)
layout.addWidget(switch_styled)
layout.addWidget(QRectangleToggleSwitch("rectangle"))
layout.addWidget(QToggleSwitchWithText("with text"))
widget.show()
app.exec()
