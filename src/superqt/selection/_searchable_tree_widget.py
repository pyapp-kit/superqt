import logging
from typing import Any, Iterable, Mapping

from qtpy.QtCore import QRegularExpression, Qt
from qtpy.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class QSearchableTreeWidget(QWidget):
    """A tree widget for showing a mapping that can be searched by key.

    This is intended to be used with a read-only mapping and be conveniently
    created using `QSearchableTreeWidget.fromMapping(data)`.
    If the mapping changes, the easiest way to update this is by calling `setData`.

    The tree can be searched by entering a regular expression pattern
    into the `filter_widget` line edit. An item is only shown if its key
    or any of its ancestors' or descendants' keys match this pattern.

    Attributes
    ----------
    tree_widget : QTreeWidget
        Shows the mapping as a tree of items.
    filter_widget : QLineEdit
        Used to filter items in the tree by matching their key against a
        regular expression.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree_widget: QTreeWidget = QTreeWidget(self)
        self.tree_widget.setHeaderLabels(("Key", "Value"))
        self.tree_widget.setUniformRowHeights(True)

        self.filter_widget: QLineEdit = QLineEdit(self)
        self.filter_widget.textChanged.connect(self._updateVisibleItems)

        layout = QVBoxLayout(self)
        layout.addWidget(self.filter_widget)
        layout.addWidget(self.tree_widget)

    def setData(self, data: Mapping) -> None:
        """Update the mapping data shown by the tree."""
        self.tree_widget.clear()
        self.filter_widget.clear()
        top_level_items = [_make_item(name=k, value=v) for k, v in data.items()]
        self.tree_widget.addTopLevelItems(top_level_items)

    def _updateVisibleItems(self, pattern: str) -> None:
        """Recursively update the visibility of the items in the tree based on the given pattern."""
        expression = QRegularExpression(pattern)
        for i in range(self.tree_widget.topLevelItemCount()):
            top_level_item = self.tree_widget.topLevelItem(i)
            _update_visible_items(top_level_item, expression)

    @classmethod
    def fromData(
        cls, data: Mapping, *, parent: QWidget = None
    ) -> "QSearchableTreeWidget":
        """Make a searchable tree widget from a mapping."""
        widget = cls(parent)
        widget.setData(data)
        return widget


def _make_item(*, name: str, value: Any) -> QTreeWidgetItem:
    """Make a tree item where the name and value are two columns.

    Iterable values other than strings are recursively traversed to
    add child items and build a tree. In this case, mappings use keys
    as their names whereas other iterables use their enumerated index.
    """
    if isinstance(value, Mapping):
        item = QTreeWidgetItem([name, type(value).__name__])
        for k, v in value.items():
            child = _make_item(name=k, value=v)
            item.addChild(child)
    elif isinstance(value, Iterable) and not isinstance(value, str):
        item = QTreeWidgetItem([name, type(value).__name__])
        for i, v in enumerate(value):
            child = _make_item(name=str(i), value=v)
            item.addChild(child)
    else:
        item = QTreeWidgetItem([name, str(value)])
        item.setFlags(item.flags() | Qt.ItemNeverHasChildren)
    logging.debug("_make_item: %s, %s, %s", item.text(0), item.text(1), item.flags())
    return item


def _update_visible_items(
    item: QTreeWidgetItem, expression: QRegularExpression, parent_visible: bool = False
) -> bool:
    """Recursively update the visibility of a tree item based on a expression.

    An item is visible if it, its parent, or any of its descendants match the expression.
    The text of the item's first column is used to match the expression.
    Returns True if the item is visible, False otherwise.
    """
    text = item.text(0)
    visible = parent_visible or expression.match(text).hasMatch()
    for i in range(item.childCount()):
        child = item.child(i)
        descendants_visible = _update_visible_items(child, expression, visible)
        visible = visible or descendants_visible
    item.setHidden(not visible)
    logging.debug("_update_visible_items: %s, %s", text, visible)
    return visible
