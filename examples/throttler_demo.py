"""Adapted for python from the KDToolBox.

https://github.com/KDAB/KDToolBox/tree/master/qt/KDSignalThrottler

MIT License

Copyright (C) 2019-2022 Klarälvdalens Datakonsult AB, a KDAB Group company,
info@kdab.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

from collections import deque

from qtpy.QtCore import QRect, QSize, Qt, QTimer, Signal
from qtpy.QtGui import QPainter, QPen
from qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from superqt.utils._throttler import (
    GenericSignalThrottler,
    QSignalDebouncer,
    QSignalThrottler,
)


class DrawSignalsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        self._scrollTimer = QTimer(self)
        self._scrollTimer.setInterval(10)
        self._scrollTimer.timeout.connect(self._scroll)
        self._scrollTimer.start()

        self._signalActivations: deque[int] = deque()
        self._throttledSignalActivations: deque[int] = deque()

    def sizeHint(self):
        return QSize(400, 200)

    def addSignalActivation(self):
        self._signalActivations.appendleft(0)

    def addThrottledSignalActivation(self):
        self._throttledSignalActivations.appendleft(0)

    def _scroll(self):
        cutoff = self.width()
        self.scrollAndCut(self._signalActivations, cutoff)
        self.scrollAndCut(self._throttledSignalActivations, cutoff)

        self.update()

    def scrollAndCut(self, v: deque[int], cutoff: int):
        L = len(v)
        for p in range(L):
            v[p] += 1
            if v[p] > cutoff:
                break

        # TODO: fix this... delete old ones

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.white)

        h = self.height()
        h2 = h // 2
        w = self.width()

        self._drawSignals(p, self._signalActivations, Qt.red, 0, h2)
        self._drawSignals(p, self._throttledSignalActivations, Qt.blue, h2, h)

        p.drawText(
            QRect(0, 0, w, h2),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "Source signal",
        )
        p.drawText(
            QRect(0, h2, w, h2),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "Throttled signal",
        )

        p.save()
        pen = QPen()
        pen.setWidthF(2.0)
        p.drawLine(0, h2, w, h2)
        p.restore()

    def _drawSignals(self, p: QPainter, v: deque[int], color, yStart, yEnd):
        p.save()
        pen = QPen()
        pen.setWidthF(2.0)
        pen.setColor(color)
        p.setPen(pen)

        for i in v:
            p.drawLine(i, yStart, i, yEnd)
        p.restore()


class DemoWidget(QWidget):
    signalToBeThrottled = Signal()
    _throttler: GenericSignalThrottler

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._createUi()
        self._throttler = None

        self._throttlerKindComboBox.currentIndexChanged.connect(self._createThrottler)
        self._createThrottler()

        self._throttlerTimeoutSpinBox.valueChanged.connect(self.setThrottlerTimeout)
        self.setThrottlerTimeout()

        self._mainButton.clicked.connect(self.signalToBeThrottled)

        self._autoTriggerTimer = QTimer(self)
        self._autoTriggerTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self._autoTriggerCheckBox.clicked.connect(self._startOrStopAutoTriggerTimer)
        self._startOrStopAutoTriggerTimer()

        self._autoTriggerIntervalSpinBox.valueChanged.connect(
            self._setAutoTriggerTimeout
        )
        self._setAutoTriggerTimeout()

        self._autoTriggerTimer.timeout.connect(self.signalToBeThrottled)
        self.signalToBeThrottled.connect(self._drawSignalsWidget.addSignalActivation)

    def _createThrottler(self) -> None:
        if self._throttler is not None:
            self._throttler.deleteLater()
            del self._throttler

        if self._throttlerKindComboBox.currentIndex() < 2:
            cls = QSignalThrottler
        else:
            cls = QSignalDebouncer
        if self._throttlerKindComboBox.currentIndex() % 2:
            policy = QSignalThrottler.EmissionPolicy.Leading
        else:
            policy = QSignalThrottler.EmissionPolicy.Trailing

        self._throttler: GenericSignalThrottler = cls(policy, self)

        self._throttler.setTimerType(Qt.TimerType.PreciseTimer)
        self.signalToBeThrottled.connect(self._throttler.throttle)
        self._throttler.triggered.connect(
            self._drawSignalsWidget.addThrottledSignalActivation
        )

        self.setThrottlerTimeout()

    def setThrottlerTimeout(self):
        self._throttler.setTimeout(self._throttlerTimeoutSpinBox.value())

    def _startOrStopAutoTriggerTimer(self):
        shouldStart = self._autoTriggerCheckBox.isChecked()
        if shouldStart:
            self._autoTriggerTimer.start()
        else:
            self._autoTriggerTimer.stop()

        self._autoTriggerIntervalSpinBox.setEnabled(shouldStart)
        self._autoTriggerLabel.setEnabled(shouldStart)

    def _setAutoTriggerTimeout(self):
        timeout = self._autoTriggerIntervalSpinBox.value()
        self._autoTriggerTimer.setInterval(timeout)

    def _createUi(self):
        helpLabel = QLabel(self)
        helpLabel.setWordWrap(True)
        helpLabel.setText(
            "<h2>SignalThrottler example</h2>"
            "<p>This example demonstrates the differences between "
            "the different kinds of signal throttlers and debouncers."
        )

        throttlerKindGroupBox = QGroupBox("Throttler configuration", self)

        self._throttlerKindComboBox = QComboBox(throttlerKindGroupBox)
        self._throttlerKindComboBox.addItems(
            (
                "Throttler, trailing",
                "Throttler, leading",
                "Debouncer, trailing",
                "Debouncer, leading",
            )
        )

        self._throttlerTimeoutSpinBox = QSpinBox(throttlerKindGroupBox)
        self._throttlerTimeoutSpinBox.setRange(1, 5000)
        self._throttlerTimeoutSpinBox.setValue(500)
        self._throttlerTimeoutSpinBox.setSuffix(" ms")

        layout = QFormLayout(throttlerKindGroupBox)
        layout.addRow("Kind of throttler:", self._throttlerKindComboBox)
        layout.addRow("Timeout:", self._throttlerTimeoutSpinBox)
        throttlerKindGroupBox.setLayout(layout)

        buttonGroupBox = QGroupBox("Throttler activation")
        self._mainButton = QPushButton(("Press me!"), buttonGroupBox)

        self._autoTriggerCheckBox = QCheckBox("Trigger automatically")

        autoTriggerLayout = QHBoxLayout()
        self._autoTriggerLabel = QLabel("Interval", buttonGroupBox)
        self._autoTriggerIntervalSpinBox = QSpinBox(buttonGroupBox)
        self._autoTriggerIntervalSpinBox.setRange(1, 5000)
        self._autoTriggerIntervalSpinBox.setValue(100)
        self._autoTriggerIntervalSpinBox.setSuffix(" ms")

        autoTriggerLayout.setContentsMargins(0, 0, 0, 0)
        autoTriggerLayout.addWidget(self._autoTriggerLabel)
        autoTriggerLayout.addWidget(self._autoTriggerIntervalSpinBox)

        layout = QVBoxLayout(buttonGroupBox)
        layout.addWidget(self._mainButton)
        layout.addWidget(self._autoTriggerCheckBox)
        layout.addLayout(autoTriggerLayout)
        buttonGroupBox.setLayout(layout)

        resultGroupBox = QGroupBox("Result")
        self._drawSignalsWidget = DrawSignalsWidget(resultGroupBox)
        layout = QVBoxLayout(resultGroupBox)
        layout.addWidget(self._drawSignalsWidget)
        resultGroupBox.setLayout(layout)

        layout = QVBoxLayout(self)
        layout.addWidget(helpLabel)
        layout.addWidget(throttlerKindGroupBox)
        layout.addWidget(buttonGroupBox)
        layout.addWidget(resultGroupBox)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([__name__])
    w = DemoWidget()
    w.resize(600, 600)
    w.show()
    app.exec_()
