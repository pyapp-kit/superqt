from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt

from superqt.fonticon._plugins import loaded

P = loaded(load_all=True)
if not P:
    print("you have no font packs loaded!")


class GlyphDelegate(QtWidgets.QItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() < 2:
            edit = QtWidgets.QLineEdit(parent)
            edit.editingFinished.connect(self.emitCommitData)
            return edit
        comboBox = QtWidgets.QComboBox(parent)
        if index.column() == 2:
            comboBox.addItem("Normal")
            comboBox.addItem("Active")
            comboBox.addItem("Disabled")
            comboBox.addItem("Selected")
        elif index.column() == 3:
            comboBox.addItem("Off")
            comboBox.addItem("On")

        comboBox.activated.connect(self.emitCommitData)
        return comboBox

    def setEditorData(self, editor, index):
        if index.column() < 2:
            editor.setText(index.model().data(index))
            return
        comboBox = editor
        if comboBox:
            pos = comboBox.findText(
                index.model().data(index), Qt.MatchFlag.MatchExactly
            )
            comboBox.setCurrentIndex(pos)

    def setModelData(self, editor, model, index):
        if editor:
            text = editor.text() if index.column() < 2 else editor.currentText()
            model.setData(index, text)

    def emitCommitData(self):
        self.commitData.emit(self.sender())


class IconPreviewArea(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        mainLayout = QtWidgets.QGridLayout()
        self.setLayout(mainLayout)

        self.icon = QtGui.QIcon()
        self.size = QtCore.QSize()
        self.stateLabels = []
        self.modeLabels = []
        self.pixmapLabels = []

        self.stateLabels.append(self.createHeaderLabel("Off"))
        self.stateLabels.append(self.createHeaderLabel("On"))
        self.modeLabels.append(self.createHeaderLabel("Normal"))
        self.modeLabels.append(self.createHeaderLabel("Active"))
        self.modeLabels.append(self.createHeaderLabel("Disabled"))
        self.modeLabels.append(self.createHeaderLabel("Selected"))

        for j, label in enumerate(self.stateLabels):
            mainLayout.addWidget(label, j + 1, 0)

        for i, label in enumerate(self.modeLabels):
            mainLayout.addWidget(label, 0, i + 1)

            self.pixmapLabels.append([])
            for j in range(len(self.stateLabels)):
                self.pixmapLabels[i].append(self.createPixmapLabel())
                mainLayout.addWidget(self.pixmapLabels[i][j], j + 1, i + 1)

    def setIcon(self, icon):
        self.icon = icon
        self.updatePixmapLabels()

    def setSize(self, size):
        if size != self.size:
            self.size = size
            self.updatePixmapLabels()

    def createHeaderLabel(self, text):
        label = QtWidgets.QLabel(f"<b>{text}</b>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def createPixmapLabel(self):
        label = QtWidgets.QLabel()
        label.setEnabled(False)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFrameShape(QtWidgets.QFrame.Box)
        label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        label.setBackgroundRole(QtGui.QPalette.Base)
        label.setAutoFillBackground(True)
        label.setMinimumSize(132, 132)
        return label

    def updatePixmapLabels(self):
        for i in range(len(self.modeLabels)):
            if i == 0:
                mode = QtGui.QIcon.Mode.Normal
            elif i == 1:
                mode = QtGui.QIcon.Mode.Active
            elif i == 2:
                mode = QtGui.QIcon.Mode.Disabled
            else:
                mode = QtGui.QIcon.Mode.Selected

            for j in range(len(self.stateLabels)):
                state = {True: QtGui.QIcon.State.Off, False: QtGui.QIcon.State.On}[
                    j == 0
                ]
                pixmap = self.icon.pixmap(self.size, mode, state)
                self.pixmapLabels[i][j].setPixmap(pixmap)
                self.pixmapLabels[i][j].setEnabled(not pixmap.isNull())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)

        self.createPreviewGroupBox()
        self.createGlyphBox()
        self.createIconSizeGroupBox()

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.previewGroupBox, 0, 0, 1, 2)
        mainLayout.addWidget(self.glyphGroupBox, 1, 0)
        mainLayout.addWidget(self.iconSizeGroupBox, 1, 1)
        self.centralWidget.setLayout(mainLayout)

        self.setWindowTitle("Icons")
        self.otherRadioButton.click()

        self.resize(self.minimumSizeHint())

    def changeSize(self):
        if self.otherRadioButton.isChecked():
            extent = self.otherSpinBox.value()
        else:
            if self.smallRadioButton.isChecked():
                metric = QtWidgets.QStyle.PixelMetric.PM_SmallIconSize
            elif self.largeRadioButton.isChecked():
                metric = QtWidgets.QStyle.PixelMetric.PM_LargeIconSize
            elif self.toolBarRadioButton.isChecked():
                metric = QtWidgets.QStyle.PixelMetric.PM_ToolBarIconSize
            elif self.listViewRadioButton.isChecked():
                metric = QtWidgets.QStyle.PixelMetric.PM_ListViewIconSize
            elif self.iconViewRadioButton.isChecked():
                metric = QtWidgets.QStyle.PixelMetric.PM_IconViewIconSize
            else:
                metric = QtWidgets.QStyle.PixelMetric.PM_TabBarIconSize

            extent = QtWidgets.QApplication.style().pixelMetric(metric)

        self.previewArea.setSize(QtCore.QSize(extent, extent))
        self.otherSpinBox.setEnabled(self.otherRadioButton.isChecked())

    def changeIcon(self):
        from superqt import fonticon

        icon = None
        for row in range(self.glyphTable.rowCount()):
            item0 = self.glyphTable.item(row, 0)
            item1 = self.glyphTable.item(row, 1)
            item2 = self.glyphTable.item(row, 2)
            item3 = self.glyphTable.item(row, 3)

            if item0.checkState() != Qt.CheckState.Checked:
                continue
            key = item0.text()
            if not key:
                continue

            if item2.text() == "Normal":
                mode = QtGui.QIcon.Mode.Normal
            elif item2.text() == "Active":
                mode = QtGui.QIcon.Mode.Active
            elif item2.text() == "Disabled":
                mode = QtGui.QIcon.Mode.Disabled
            else:
                mode = QtGui.QIcon.Mode.Selected

            color = item1.text() or None
            state = (
                QtGui.QIcon.State.On if item3.text() == "On" else QtGui.QIcon.State.Off
            )
            try:
                if icon is None:
                    icon = fonticon.icon(key, color=color)
                else:
                    icon.addState(state, mode, glyph_key=key, color=color)
            except Exception as e:
                print(e)
                continue
        if icon:
            self.previewArea.setIcon(icon)

    def createPreviewGroupBox(self):
        self.previewGroupBox = QtWidgets.QGroupBox("Preview")

        self.previewArea = IconPreviewArea()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.previewArea)
        self.previewGroupBox.setLayout(layout)

    def createGlyphBox(self):
        self.glyphGroupBox = QtWidgets.QGroupBox("Glyphs")
        self.glyphGroupBox.setMinimumSize(480, 200)
        self.glyphTable = QtWidgets.QTableWidget()
        self.glyphTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.glyphTable.setItemDelegate(GlyphDelegate(self))

        self.glyphTable.horizontalHeader().setDefaultSectionSize(100)
        self.glyphTable.setColumnCount(4)
        self.glyphTable.setHorizontalHeaderLabels(("Glyph", "Color", "Mode", "State"))
        self.glyphTable.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.glyphTable.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Fixed
        )
        self.glyphTable.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Fixed
        )
        self.glyphTable.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Fixed
        )
        self.glyphTable.verticalHeader().hide()

        self.glyphTable.itemChanged.connect(self.changeIcon)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.glyphTable)
        self.glyphGroupBox.setLayout(layout)
        self.changeIcon()

        p0 = list(P)[-1]
        key = f"{p0}.{list(P[p0])[1]}"
        for _ in range(4):
            row = self.glyphTable.rowCount()
            self.glyphTable.setRowCount(row + 1)

            item0 = QtWidgets.QTableWidgetItem()
            item1 = QtWidgets.QTableWidgetItem()

            if _ == 0:
                item0.setText(key)
            # item0.setFlags(item0.flags() & ~Qt.ItemFlag.ItemIsEditable)

            item2 = QtWidgets.QTableWidgetItem("Normal")
            item3 = QtWidgets.QTableWidgetItem("Off")

            self.glyphTable.setItem(row, 0, item0)
            self.glyphTable.setItem(row, 1, item1)
            self.glyphTable.setItem(row, 2, item2)
            self.glyphTable.setItem(row, 3, item3)
            self.glyphTable.openPersistentEditor(item2)
            self.glyphTable.openPersistentEditor(item3)

            item0.setCheckState(Qt.CheckState.Checked)

    def createIconSizeGroupBox(self):
        self.iconSizeGroupBox = QtWidgets.QGroupBox("Icon Size")

        self.smallRadioButton = QtWidgets.QRadioButton()
        self.largeRadioButton = QtWidgets.QRadioButton()
        self.toolBarRadioButton = QtWidgets.QRadioButton()
        self.listViewRadioButton = QtWidgets.QRadioButton()
        self.iconViewRadioButton = QtWidgets.QRadioButton()
        self.tabBarRadioButton = QtWidgets.QRadioButton()
        self.otherRadioButton = QtWidgets.QRadioButton("Other:")

        self.otherSpinBox = QtWidgets.QSpinBox()
        self.otherSpinBox.setRange(8, 128)
        self.otherSpinBox.setValue(64)

        self.smallRadioButton.toggled.connect(self.changeSize)
        self.largeRadioButton.toggled.connect(self.changeSize)
        self.toolBarRadioButton.toggled.connect(self.changeSize)
        self.listViewRadioButton.toggled.connect(self.changeSize)
        self.iconViewRadioButton.toggled.connect(self.changeSize)
        self.tabBarRadioButton.toggled.connect(self.changeSize)
        self.otherRadioButton.toggled.connect(self.changeSize)
        self.otherSpinBox.valueChanged.connect(self.changeSize)

        otherSizeLayout = QtWidgets.QHBoxLayout()
        otherSizeLayout.addWidget(self.otherRadioButton)
        otherSizeLayout.addWidget(self.otherSpinBox)
        otherSizeLayout.addStretch()

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.smallRadioButton, 0, 0)
        layout.addWidget(self.largeRadioButton, 1, 0)
        layout.addWidget(self.toolBarRadioButton, 2, 0)
        layout.addWidget(self.listViewRadioButton, 0, 1)
        layout.addWidget(self.iconViewRadioButton, 1, 1)
        layout.addWidget(self.tabBarRadioButton, 2, 1)
        layout.addLayout(otherSizeLayout, 3, 0, 1, 2)
        layout.setRowStretch(4, 1)
        self.iconSizeGroupBox.setLayout(layout)
        self.changeStyle()

    def changeStyle(self, style=None):
        style = style or QtWidgets.QApplication.style().objectName()
        style = QtWidgets.QStyleFactory.create(style)
        if not style:
            return

        QtWidgets.QApplication.setStyle(style)

        self.setButtonText(
            self.smallRadioButton,
            "Small (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_SmallIconSize,
        )
        self.setButtonText(
            self.largeRadioButton,
            "Large (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_LargeIconSize,
        )
        self.setButtonText(
            self.toolBarRadioButton,
            "Toolbars (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_ToolBarIconSize,
        )
        self.setButtonText(
            self.listViewRadioButton,
            "List views (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_ListViewIconSize,
        )
        self.setButtonText(
            self.iconViewRadioButton,
            "Icon views (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_IconViewIconSize,
        )
        self.setButtonText(
            self.tabBarRadioButton,
            "Tab bars (%d x %d)",
            style,
            QtWidgets.QStyle.PixelMetric.PM_TabBarIconSize,
        )

        self.changeSize()

    @staticmethod
    def setButtonText(button, label, style, metric):
        metric_value = style.pixelMetric(metric)
        button.setText(label % (metric_value, metric_value))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
