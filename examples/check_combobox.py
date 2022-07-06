from qtpy.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from superqt import QCheckComboBox


def change_label_type() -> None:
    """Function used to swtich the label type"""
    if combobox.labelType() == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS:
        combobox.setLabelType(QCheckComboBox.QCheckComboBoxLabelType.STRING)
        combobox.setLabelText("Select Sample")
    else:
        combobox.setLabelType(QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS)


# Create main window
app = QApplication([])
main_window = QMainWindow()
main_widget = QWidget()
main_layout = QVBoxLayout()
main_window.setFixedWidth(700)
main_window.setFixedHeight(450)

# Create the check comobobox
combobox = QCheckComboBox()
combobox.setLabelText("Select items")
texts = [f"Item {i}" for i in range(5)]
combobox.addItems(texts)

# Add button to change the label type
button = QPushButton("Change label type")
button.clicked.connect(lambda: change_label_type())

# Add widgets to main window
main_widget.setLayout(main_layout)
main_widget.layout().addWidget(combobox)
main_widget.layout().addWidget(button)
main_window.setCentralWidget(main_widget)
main_window.show()

# Run
app.exec_()
