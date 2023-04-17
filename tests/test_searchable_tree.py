from typing import Any, List
import pytest
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
from pytestqt.qtbot import QtBot
from superqt import QSearchableTreeWidget


@pytest.fixture
def data() -> dict:
    return {
        'none': None,
        'str': 'test',
        'int': 42,
        'list': [2, 3, 5],
        'dict': {
            'float': 0.5,
            'tuple': (22, 99),
        },
    }


@pytest.fixture
def widget(qtbot: QtBot, data: dict) -> QSearchableTreeWidget:
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    return widget


def assert_item_equal(item: QTreeWidgetItem, key: str, value: Any):
    assert item.text(0) == key
    assert item.text(1) == str(value)


def get_all_items(tree: QTreeWidget) -> List[QTreeWidgetItem]:
    return tree.findItems('', Qt.MatchContains | Qt.MatchRecursive)


def get_shown_items(tree: QTreeWidget) -> List[QTreeWidgetItem]:
    all_items = get_all_items(tree)
    return [item for item in all_items if not item.isHidden()]


def test_init(qtbot: QtBot):
    widget = QSearchableTreeWidget()
    qtbot.addWidget(widget)
    assert widget.tree_widget.topLevelItemCount() == 0


def test_from_data(qtbot: QtBot, data: dict):
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    tree = widget.tree_widget

    assert tree.topLevelItemCount() == 5

    none_item = tree.topLevelItem(0)
    assert_item_equal(none_item, 'none', None)
    assert none_item.childCount() == 0

    str_item = tree.topLevelItem(1)
    assert_item_equal(str_item, 'str', 'test')
    assert str_item.childCount() == 0

    int_item = tree.topLevelItem(2)
    assert_item_equal(int_item, 'int', 42)
    assert int_item.childCount() == 0
    
    list_item = tree.topLevelItem(3)
    assert_item_equal(list_item, 'list', [2, 3, 5])
    assert list_item.childCount() == 3
    assert_item_equal(list_item.child(0), '0', 2)
    assert_item_equal(list_item.child(1), '1', 3)
    assert_item_equal(list_item.child(2), '2', 5)

    dict_item = tree.topLevelItem(4)
    assert_item_equal(dict_item, 'dict', {'float': 0.5, 'tuple': (22, 99)})
    assert dict_item.childCount() == 2
    assert_item_equal(dict_item.child(0), 'float', 0.5)
    tuple_item = dict_item.child(1)
    assert_item_equal(tuple_item, 'tuple', (22, 99))
    assert tuple_item.childCount() == 2
    assert_item_equal(tuple_item.child(0), '0', 22)
    assert_item_equal(tuple_item.child(1), '1', 99)


def test_set_data(widget: QSearchableTreeWidget):
    tree = widget.tree_widget
    assert tree.topLevelItemCount() != 1

    widget.setData({'test': 'reset'})

    assert tree.topLevelItemCount() == 1
    assert_item_equal(tree.topLevelItem(0), 'test', 'reset')


def test_search_no_match(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('no match here')
    shown_items = get_shown_items(widget.tree_widget)
    assert len(shown_items) == 0


def test_search_all_match(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('')
    all_items = get_all_items(widget.tree_widget)
    shown_items = get_shown_items(widget.tree_widget)
    assert all_items == shown_items


def test_search_match_one(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('int')
    shown_items = get_shown_items(widget.tree_widget)
    assert len(shown_items) == 1
    assert_item_equal(shown_items[0], 'int', 42)


def test_search_match_many(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('n')
    shown_items = get_shown_items(widget.tree_widget)
    assert len(shown_items) == 2
    assert_item_equal(shown_items[0], 'none', None)
    assert_item_equal(shown_items[1], 'int', 42)


def test_search_match_one_show_unmatched_descendants(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('list')
    shown_items = get_shown_items(widget.tree_widget)
    assert len(shown_items) == 4
    assert_item_equal(shown_items[0], 'list', [2, 3, 5])
    assert_item_equal(shown_items[1], '0', 2)
    assert_item_equal(shown_items[2], '1', 3)
    assert_item_equal(shown_items[3], '2', 5)


def test_search_match_one_show_unmatched_ancestors(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('tuple')
    shown_items = get_shown_items(widget.tree_widget)
    assert len(shown_items) == 4
    assert_item_equal(shown_items[0], 'dict', {'float': 0.5, 'tuple': (22, 99)})
    assert_item_equal(shown_items[1], 'tuple', (22, 99))
    assert_item_equal(shown_items[2], '0', 22)
    assert_item_equal(shown_items[3], '1', 99)
