"""A QAbstractItemModel designed to work with
`psygnal.containers.SelectableEventedList`.
"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from psygnal.containers import SelectableEventedList
from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget

ItemType = TypeVar("ItemType")
ItemRole = Qt.UserRole
SortRole = Qt.UserRole + 1

_BASE_FLAGS = (
    Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEditable
    | Qt.ItemFlag.ItemIsUserCheckable
    | Qt.ItemFlag.ItemIsDragEnabled
    | Qt.ItemFlag.ItemIsEnabled
)


class _BaseEventedItemModel(QAbstractItemModel, Generic[ItemType]):
    """A QAbstractItemModel designed to work with
    `psygnal.containers.SelectableEventedList`.

    `SelectableEventedList` is a model for a Python list which supports the
    concept of "currently selected/active items".

    This module contains a class which acts as an adapter between the
    `SelectableEventedList` and Qt's `QAbstractItemModel` interface (see `Qt
    Model/View Programming <https://doc.qt.io/qt-6/modelview.html>`_). In
    this way, it allows Python users to interact with the list in the "usual"
    Python ways and simultaneously updates any Qt views onto the list model.
    Conversely, it also updates the list model if any GUI events occur in the
    view.
    """

    _root: SelectableEventedList[ItemType]

    def __init__(self, root: SelectableEventedList[ItemType], parent: QWidget = None):
        super().__init__(parent=parent)
        self.setRoot(root)

    def parent(self, index: QModelIndex):
        """Return the parent of the model item with the given `index`.

        (The parent in a basic list is always the root, Tree models will need
        to reimplement)
        """
        return QModelIndex()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Returns data stored under `role` for the item at `index`.

        A given `QModelIndex can store multiple types of data, each with its
        own `ItemDataRole`. ItemType-specific subclasses will likely want to
        customize this method (and likely `setData` too) for different data
        roles.

        see: https://doc.qt.io/qt-6/qt.html#ItemDataRole-enum
        """
        if role == Qt.DisplayRole:
            return str(self.getItem(index))
        if role == ItemRole:
            return self.getItem(index)
        if role == SortRole:
            return index.row()
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Returns the item flags for the given `index`.

        This describes the properties of a given item in the model. We set
        them to be editable, checkable, draggable, droppable, etc...
        If index is not a list, we additionally set `Qt.ItemNeverHasChildren`
        (for optimization). Editable models must return a value containing
        `Qt.ItemIsEditable`.

        See Qt.ItemFlags https://doc.qt.io/qt-6/qt.html#ItemFlag-enum
        """
        if not index.isValid() or index.model() is not self:
            # we allow drops outside the items
            return Qt.ItemFlag.ItemIsDropEnabled
        if isinstance(self.getItem(index), MutableSequence):
            return _BASE_FLAGS | Qt.ItemFlag.ItemIsDropEnabled
        return _BASE_FLAGS | Qt.ItemFlag.ItemNeverHasChildren

    def columnCount(self, parent: QModelIndex) -> int:
        """Return the number of columns for the children of the given `parent`.

        In a list view, and most tree views, the number of columns is 1.
        """
        return 1

    def rowCount(self, parent: QModelIndex = None) -> int:
        """Returns the number of rows under the given `parent`.

        When the parent is valid it means that rowCount is returning the number
        of children of parent.
        """
        if parent is None:
            parent = QModelIndex()
        try:
            return len(self.getItem(parent))
        except TypeError:
            return 0

    def index(
        self, row: int, column: int = 0, parent: QModelIndex = None
    ) -> QModelIndex:
        """Return a QModelIndex for the item at `row`, `column` and `parent`."""
        # NOTE: the use of `self.createIndex(row, col, object)`` will create a
        # model index that stores a pointer to the object, which can be
        # retrieved later with index.internalPointer().  That's convenient and
        # performant, and very important tree structures, but it causes a bug
        # if integers (or perhaps values that get garbage collected?) are in
        # the list, because `createIndex` is an overloaded function and
        # `self.createIndex(row, col, <int>)` will assume that the third
        # argument *is* the id of the object (not the object itself).  This
        # will then cause a segfault if `index.internalPointer()` is used
        # later.

        # so we need to either:
        #   1. refuse store integers in this model
        #   2. never store the object (and incur the penalty of
        #      self.getItem(idx) each time you want to get the value of an idx)
        #   3. Have special treatment when we encounter integers in the model
        #   4. Wrap every object in *another* object (which is basically what
        #      Qt does with QAbstractItem)... ugh.
        #
        # Unfortunately, all of those come at a cost... as this is a very
        # frequently called function :/
        if parent is None:
            parent = QModelIndex()
        return (
            self.createIndex(row, column, self.getItem(parent)[row])
            if self.hasIndex(row, column, parent)
            else QModelIndex()  # instead of index error, Qt wants null index
        )

    def supportedDropActions(self) -> Qt.DropActions:
        """Returns the drop actions supported by this model.

        The default implementation returns `Qt.CopyAction`. We re-implemented to
        support only `Qt.MoveAction`. See also dropMimeData(), which must handle
        each supported drop action type.
        """
        return Qt.MoveAction

    def setRoot(self, root: SelectableEventedList[ItemType]):
        """Call during __init__, to set the Python model and connecions."""
        if not isinstance(root, SelectableEventedList):
            raise TypeError(f"root must be an instance of {SelectableEventedList}")
        current_root = getattr(self, "_root", None)
        if root is current_root:
            return
        if current_root is not None:
            for signal in root.events.signals.values():
                signal.disconnect()

        self._root = root
        self._root.events.removing.connect(self._on_begin_moving)
        self._root.events.removed.connect(self._on_end_move)
        self._root.events.inserting.connect(self._on_begin_inserting)
        self._root.events.inserted.connect(self._on_end_insert)
        self._root.events.moving.connect(self._on_begin_moving)
        self._root.events.moved.connect(self._on_end_move)

    def _split_nested_index(
        self, index: int | tuple[int, ...]
    ) -> tuple[QModelIndex, int]:
        """Return (parent_index, row) for a given `index`.

        Tuple indexes are used in `NestableEventedList`, we support them here
        so that subclasses needn't reimplement our _on_begin_* methods.
        """
        if isinstance(index, int):
            return QModelIndex(), index
        parent_index = QModelIndex()
        *_p, idx = index
        for i in _p:
            parent_index = self.index(i, 0, parent_index)
        return parent_index, index

    def _on_begin_inserting(self, index: int | tuple[int, ...]) -> None:
        """Begins a row insertion operation.

        See Qt documentation:
        https://doc.qt.io/qt-6/qabstractitemmodel.html#beginInsertRows
        """
        parent_index, index = self._split_nested_index(index)
        self.beginInsertRows(parent_index, index, index)

    def _on_end_insert(self, index: int | tuple[int, ...], value: Any) -> None:
        """Must be called after insert operatios to update model."""
        self.endInsertRows()

    def _on_begin_removing(self, index: int | tuple[int, ...]) -> None:
        """Begins a row removal operation.

        See Qt documentation:
        https://doc.qt.io/qt-6/qabstractitemmodel.html#beginRemoveRows
        """
        parent_index, index = self._split_nested_index(index)
        self.beginRemoveRows(parent_index, index, index)

    def _on_end_remove(self, index: int | tuple[int, ...], value: Any) -> None:
        """Must be called after row removal to update model."""
        self.endRemoveRows()

    def _on_begin_moving(self, index: int | tuple[int, ...]) -> None:
        """Begins a row move operation.

        See Qt documentation:
        https://doc.qt.io/qt-6/qabstractitemmodel.html#beginMoveRows
        """
        src_parent, src_index = self._split_nested_index(index)
        dest_parent, dest_index = self._split_nested_index(index)
        self.beginMoveRows(src_parent, src_index, dest_parent, dest_index)

    def _on_end_move(self, indexes: tuple, value: Any) -> None:
        """Must be called after move operation to update model."""
        self.endMoveRows()

    def getItem(self, index: QModelIndex) -> ItemType:
        """Return Python object for a given `index`.

        An invalid index (`QModelIndex`) will return the root object.
        """
        return self._root[index.row()] if index.isValid() else self._root
