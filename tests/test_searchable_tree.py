import pytest
from pytestqt.qtbot import QtBot
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QTreeWidget, QTreeWidgetItem

from superqt import QSearchableTreeWidget


@pytest.fixture
def data() -> dict:
    return {
        "none": None,
        "str": "test",
        "int": 42,
        "list": [2, 3, 5],
        "dict": {
            "float": 0.5,
            "tuple": (22, 99),
            "bool": False,
        },
    }


@pytest.fixture
def widget(qtbot: QtBot, data: dict) -> QSearchableTreeWidget:
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    return widget


def columns(item: QTreeWidgetItem) -> tuple[str, str]:
    return item.text(0), item.text(1)


def all_items(tree: QTreeWidget) -> list[QTreeWidgetItem]:
    return tree.findItems("", Qt.MatchContains | Qt.MatchRecursive)


def shown_items(tree: QTreeWidget) -> list[QTreeWidgetItem]:
    items = all_items(tree)
    return [item for item in items if not item.isHidden()]


def test_init(qtbot: QtBot):
    widget = QSearchableTreeWidget()
    qtbot.addWidget(widget)
    assert widget.tree.topLevelItemCount() == 0


def test_from_data(qtbot: QtBot, data: dict):
    widget = QSearchableTreeWidget.fromData(data)
    qtbot.addWidget(widget)
    tree = widget.tree

    assert tree.topLevelItemCount() == 5

    none_item = tree.topLevelItem(0)
    assert columns(none_item) == ("none", "None")
    assert none_item.childCount() == 0

    str_item = tree.topLevelItem(1)
    assert columns(str_item) == ("str", "test")
    assert str_item.childCount() == 0

    int_item = tree.topLevelItem(2)
    assert columns(int_item) == ("int", "42")
    assert int_item.childCount() == 0

    list_item = tree.topLevelItem(3)
    assert columns(list_item) == ("list", "list")
    assert list_item.childCount() == 3
    assert columns(list_item.child(0)) == ("0", "2")
    assert columns(list_item.child(1)) == ("1", "3")
    assert columns(list_item.child(2)) == ("2", "5")

    dict_item = tree.topLevelItem(4)
    assert columns(dict_item) == ("dict", "dict")
    assert dict_item.childCount() == 3
    assert columns(dict_item.child(0)) == ("float", "0.5")
    tuple_item = dict_item.child(1)
    assert columns(tuple_item) == ("tuple", "tuple")
    assert tuple_item.childCount() == 2
    assert columns(tuple_item.child(0)) == ("0", "22")
    assert columns(tuple_item.child(1)) == ("1", "99")
    assert columns(dict_item.child(2)) == ("bool", "False")


def test_set_data(widget: QSearchableTreeWidget):
    tree = widget.tree
    assert tree.topLevelItemCount() != 1

    widget.setData({"test": "reset"})

    assert tree.topLevelItemCount() == 1
    assert columns(tree.topLevelItem(0)) == ("test", "reset")


def test_search_no_match(widget: QSearchableTreeWidget):
    widget.filter.setText("no match here")
    items = shown_items(widget.tree)
    assert len(items) == 0


def test_search_all_match(widget: QSearchableTreeWidget):
    widget.filter.setText("")
    tree = widget.tree
    assert all_items(tree) == shown_items(tree)


def test_search_match_one_key(widget: QSearchableTreeWidget):
    widget.filter.setText("int")
    items = shown_items(widget.tree)
    assert len(items) == 1
    assert columns(items[0]) == ("int", "42")


def test_search_match_one_value(widget: QSearchableTreeWidget):
    widget.filter.setText("test")
    items = shown_items(widget.tree)
    assert len(items) == 1
    assert columns(items[0]) == ("str", "test")


def test_search_match_many_keys(widget: QSearchableTreeWidget):
    widget.filter.setText("n")
    items = shown_items(widget.tree)
    assert len(items) == 2
    assert columns(items[0]) == ("none", "None")
    assert columns(items[1]) == ("int", "42")


def test_search_match_one_show_unmatched_descendants(widget: QSearchableTreeWidget):
    widget.filter.setText("list")
    items = shown_items(widget.tree)
    assert len(items) == 4
    assert columns(items[0]) == ("list", "list")
    assert columns(items[1]) == ("0", "2")
    assert columns(items[2]) == ("1", "3")
    assert columns(items[3]) == ("2", "5")


def test_search_match_one_show_unmatched_ancestors(widget: QSearchableTreeWidget):
    widget.filter.setText("tuple")
    items = shown_items(widget.tree)
    assert len(items) == 4
    assert columns(items[0]) == ("dict", "dict")
    assert columns(items[1]) == ("tuple", "tuple")
    assert columns(items[2]) == ("0", "22")
    assert columns(items[3]) == ("1", "99")
