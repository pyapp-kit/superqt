import logging
from typing import Any

from qtpy.QtCore import QRegularExpression
from qtpy.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class QSearchableTreeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(('Key', 'Value'))

        self.filter_widget = QLineEdit()
        self.filter_widget.textChanged.connect(self.onlyShowMatchedItems)

        layout = QVBoxLayout()
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    def setData(self, data: dict) -> None:
        self.tree_widget.clear()
        top_level_items = [_to_item(k, v) for k, v in data.items()]
        self.tree_widget.addTopLevelItems(top_level_items)

    def onlyShowMatchedItems(self, text: str) -> None:
        expression = QRegularExpression(text)
        for i in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(i)
            _update_visible_items(top_level_item, expression)

    @classmethod
    def fromDict(cls, data: dict, *, parent: QWidget = None) -> 'QSearchableTreeWidget':
        widget = cls(parent)
        widget.setData(data)
        return widget


def _to_item(name: str, value: Any) -> QTreeWidgetItem:
    item = QTreeWidgetItem((name, str(value)))
    if isinstance(value, dict):
        for k, v in value.items():
            child = _to_item(k, v)
            item.addChild(child)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            child = _to_item(str(i), v)
            item.addChild(child)
    logging.debug('to_item: %s, %s', item.text(0), item.text(1))
    return item


def _update_visible_items(item: QTreeWidgetItem, expression: QRegularExpression) -> bool:
    text = item.text(0)
    is_hidden = not expression.match(text).hasMatch()
    for i in range(item.childCount()):
        child = item.child(i)
        descendants_hidden = _update_visible_items(child, expression)
        is_hidden = is_hidden and descendants_hidden
    item.setHidden(is_hidden)
    logging.debug('is_hidden: %s, %s', text, is_hidden)
    return is_hidden
