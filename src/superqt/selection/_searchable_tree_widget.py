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
        self.filter_widget.textChanged.connect(self._updateVisibleItems)

        layout = QVBoxLayout()
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    def setData(self, data: dict) -> None:
        self.tree_widget.clear()
        self.filter_widget.clear()
        top_level_items = [_to_item(k, v) for k, v in data.items()]
        self.tree_widget.addTopLevelItems(top_level_items)

    def _updateVisibleItems(self, text: str) -> None:
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
    """Recursively update the visibility of a tree item by matching against a regular expression.
    An item is visible if it or any of its descendants are visible.
    Returns True if the item is visible, False otherwise.
    """
    text = item.text(0)
    visible = expression.match(text).hasMatch()
    for i in range(item.childCount()):
        child = item.child(i)
        descendants_visible = _update_visible_items(child, expression)
        visible = visible or descendants_visible
    item.setHidden(not visible)
    logging.debug('visible: %s, %s', text, visible)
    return visible
