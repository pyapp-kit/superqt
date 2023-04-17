from typing import Any, List
import pytest
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem
from superqt import QSearchableTreeWidget


@pytest.fixture
def data() -> dict:
    return {
        'null': None,
        'string': 'test',
        'number': 42,
        'array': [2, 3, 5],
        'object': {
            'a': 1,
            'q': (22, 99),
        },
    }


@pytest.fixture
def widget(qtbot, data: dict) -> QSearchableTreeWidget:
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    return widget


def assert_item_equal(item: QTreeWidgetItem, key: str, value: Any):
    assert item.text(0) == key
    assert item.text(1) == str(value)


def get_all_items(tree: QTreeWidget) -> List[QTreeWidgetItem]:
    return tree.findItems('', Qt.MatchContains | Qt.MatchRecursive)


def test_init(qtbot):
    widget = QSearchableTreeWidget()
    qtbot.addWidget(widget)
    assert widget.tree_widget.topLevelItemCount() == 0


def test_from_data(qtbot, data: dict):
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    tree = widget.tree_widget

    assert tree.topLevelItemCount() == 5

    item_0 = tree.topLevelItem(0)
    assert_item_equal(item_0, 'null', None)
    assert item_0.childCount() == 0

    item_1 = tree.topLevelItem(1)
    assert_item_equal(item_1, 'string', 'test')
    assert item_0.childCount() == 0

    item_2 = tree.topLevelItem(2)
    assert_item_equal(item_2, 'number', 42)
    assert item_2.childCount() == 0
    
    item_3 = tree.topLevelItem(3)
    assert_item_equal(item_3, 'array', [2, 3, 5])
    assert item_3.childCount() == 3
    assert_item_equal(item_3.child(0), '0', 2)
    assert_item_equal(item_3.child(1), '1', 3)
    assert_item_equal(item_3.child(2), '2', 5)

    item_4 = tree.topLevelItem(4)
    assert_item_equal(item_4, 'object', {'a': 1, 'q': (22, 99)})
    assert item_4.childCount() == 2
    assert_item_equal(item_4.child(0), 'a', 1)
    assert_item_equal(item_4.child(1), 'q', (22, 99))
    assert item_4.child(1).childCount() == 2
    assert_item_equal(item_4.child(1).child(0), '0', 22)
    assert_item_equal(item_4.child(1).child(1), '1', 99)


def test_set_data(widget: QSearchableTreeWidget):
    tree = widget.tree_widget
    assert tree.topLevelItemCount() != 1

    widget.setData({'test': 'reset'})

    assert tree.topLevelItemCount() == 1
    assert_item_equal(tree.topLevelItem(0), 'test', 'reset')


def test_search_no_match(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('no match here')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    assert len(shown_items) == 0


def test_search_all_match(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    assert all_items == shown_items


def test_search_match_one_top_level_key(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('number')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    assert len(shown_items) == 1
    assert shown_items[0].text(0) == 'number'


def test_search_match_many_top_level_keys(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('n')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    shown_keys = set(item.text(0) for item in shown_items)
    assert {'null', 'string', 'number'} == shown_keys


def test_search_match_parent_then_show_unmatched_descendants(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('array')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    shown_keys = set(item.text(0) for item in shown_items)
    assert {'array', '0', '1', '2'} == shown_keys


def test_search_match_descendant_then_show_unmatched_ancestors(widget: QSearchableTreeWidget):
    widget.filter_widget.setText('q')
    all_items = get_all_items(widget.tree_widget)
    shown_items = [item for item in all_items if not item.isHidden()]
    shown_keys = set(item.text(0) for item in shown_items)
    assert {'object', 'q', '0', '1'} == shown_keys
