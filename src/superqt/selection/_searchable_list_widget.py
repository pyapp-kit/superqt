from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLineEdit, QListWidget, QVBoxLayout, QWidget


class QSearchableListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list_widget = QListWidget()

        self.filter_widget = QLineEdit()
        self.filter_widget.textChanged.connect(self.update_visible)

        layout = QVBoxLayout()
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def __getattr__(self, item):
        if hasattr(self.list_widget, item):
            return getattr(self.list_widget, item)
        return super().__getattr__(item)

    def update_visible(self, text):
        items_text = [
            x.text() for x in self.list_widget.findItems(text, Qt.MatchContains)
        ]
        for index in range(self.list_widget.count()):
            item = self.item(index)
            item.setHidden(item.text() not in items_text)

    def addItems(self, *args):
        self.list_widget.addItems(*args)
        self.update_visible(self.filter_widget.text())

    def addItem(self, *args):
        self.list_widget.addItem(*args)
        self.update_visible(self.filter_widget.text())

    def insertItems(self, *args):
        self.list_widget.insertItems(*args)
        self.update_visible(self.filter_widget.text())

    def insertItem(self, *args):
        self.list_widget.insertItem(*args)
        self.update_visible(self.filter_widget.text())
