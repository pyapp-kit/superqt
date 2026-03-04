import logging
from collections.abc import Iterable, Mapping
from typing import Any

from qtpy.QtCore import QRegularExpression
from qtpy.QtWidgets import QLineEdit, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class QSearchableTreeWidget(QWidget):
    """A tree widget for showing a mapping that can be searched by key.

    This is intended to be used with a read-only mapping and be conveniently
    created using `QSearchableTreeWidget.fromData(data)`.
    If the mapping changes, the easiest way to update this is by calling `setData`.

    The tree can be searched by entering a regular expression pattern
    into the `filter` line edit. An item is only shown if its, any of its ancestors',
    or any of its descendants' keys or values match this pattern.
    The regular expression follows the conventions described by the Qt docs:
    https://doc.qt.io/qt-6/qregularexpression.html#details

    Attributes
    ----------
    tree : QTreeWidget
        Shows the mapping as a tree of items.
    filter : QLineEdit
        Used to filter items in the tree by matching their key against a
        regular expression.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree: QTreeWidget = QTreeWidget(self)
        self.tree.setHeaderLabels(("Key", "Value"))

        self.filter: QLineEdit = QLineEdit(self)
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._updateVisibleItems)

        layout = QVBoxLayout(self)
        layout.addWidget(self.filter)
        layout.addWidget(self.tree)

    def setData(self, data: Mapping) -> None:
        """Update the mapping data shown by the tree."""
        self.tree.clear()
        self.filter.clear()
        top_level_items = [_make_item(name=k, value=v) for k, v in data.items()]
        self.tree.addTopLevelItems(top_level_items)

    def _updateVisibleItems(self, pattern: str) -> None:
        """Recursively update the visibility of items based on the given pattern."""
        expression = QRegularExpression(pattern)
        for i in range(self.tree.topLevelItemCount()):
            top_level_item = self.tree.topLevelItem(i)
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
    logging.debug("_make_item: %s, %s, %s", item.text(0), item.text(1), item.flags())
    return item


def _update_visible_items(
    item: QTreeWidgetItem, expression: QRegularExpression, ancestor_match: bool = False
) -> bool:
    """Recursively update the visibility of a tree item based on an expression.

    An item is visible if any of its, any of its ancestors', or any of its descendants'
    column's text matches the expression.
    Returns True if the item is visible, False otherwise.
    """
    match = ancestor_match or any(
        expression.match(item.text(i)).hasMatch() for i in range(item.columnCount())
    )
    visible = match
    for i in range(item.childCount()):
        child = item.child(i)
        descendant_visible = _update_visible_items(child, expression, match)
        visible = visible or descendant_visible
    item.setHidden(not visible)
    logging.debug(
        "_update_visible_items: %s, %s",
        tuple(item.text(i) for i in range(item.columnCount())),
        visible,
    )
    return visible
