from pytestqt.qtbot import QtBot
from qtpy.QtCore import QEvent

from superqt import QCheckComboBox


def test_add_item(qtbot: QtBot) -> None:
    """Tests the addition of item"""

    check_combobox = QCheckComboBox()
    qtbot.add_widget(check_combobox)

    check_combobox.addItem("Item 1", userData=1, checked=False)
    check_combobox.addItem("Item 2", userData="2", checked=True)

    assert check_combobox.itemData(0) == 1
    assert check_combobox.itemData(1) == "2"
    assert check_combobox.itemText(0) == "Item 1"
    assert check_combobox.itemText(1) == "Item 2"


def test_add_items(qtbot: QtBot) -> None:
    """Tests the addition of items"""

    check_combobox1 = QCheckComboBox()
    qtbot.add_widget(check_combobox1)
    check_combobox1.addItems(["Item 1", "Item 2", "Item 3"])
    assert check_combobox1.itemText(0) == "Item 1"
    assert check_combobox1.itemText(1) == "Item 2"
    assert check_combobox1.itemText(2) == "Item 3"

    check_combobox2 = QCheckComboBox()
    qtbot.add_widget(check_combobox2)
    check_combobox2.addItems(["Item 1", "Item 2"], checked=False)
    assert check_combobox2.itemChecked(0) is False
    assert check_combobox2.itemChecked(1) is False

    check_combobox3 = QCheckComboBox()
    qtbot.add_widget(check_combobox3)
    check_combobox3.addItems(["Item 1", "Item 2"], checked=True)
    assert check_combobox3.itemChecked(0) is True
    assert check_combobox3.itemChecked(1) is True

    check_combobox4 = QCheckComboBox()
    qtbot.add_widget(check_combobox4)
    check_combobox4.addItems(["Item 1", "Item 2"], checked=[True, False])
    assert check_combobox4.itemChecked(0) is True
    assert check_combobox4.itemChecked(1) is False


def test_set_all_items_checked(qtbot: QtBot) -> None:
    """Tests setting all items checked status"""
    check_combobox = QCheckComboBox()
    check_combobox.addItems(["Item 1", "Item 2", "Item 3"], checked=[True, False, True])
    checked_status = [
        check_combobox.itemChecked(i) for i in range(check_combobox.count())
    ]
    assert checked_status == [True, False, True]

    check_combobox.setAllItemChecked(False)
    checked_status = [
        check_combobox.itemChecked(i) for i in range(check_combobox.count())
    ]
    assert checked_status == [False, False, False]

    check_combobox.setAllItemChecked(True)
    checked_status = [
        check_combobox.itemChecked(i) for i in range(check_combobox.count())
    ]
    assert checked_status == [True, True, True]


def test_indices_retrival(qtbot: QtBot) -> None:
    """Tests retrival of the indices checked and unchecked"""
    check_combobox = QCheckComboBox()
    check_combobox.addItems(["Item 1", "Item 2", "Item 3"], checked=[True, False, True])
    assert check_combobox.checkedIndices() == [0, 2]
    assert check_combobox.uncheckedIndices() == [1]


def test_changing_label_string(qtbot: QtBot) -> None:
    """Tests changing the label string"""
    check_combobox = QCheckComboBox()
    check_combobox.setLabelText("Please select items")
    assert check_combobox.labelText() == "Please select items"


def test_selected_items_label_type(qtbot: QtBot) -> None:
    """Tests selected item label"""
    check_combobox = QCheckComboBox()
    check_combobox.setLabelType(QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS)
    assert (
        check_combobox.labelType()
        == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS
    )

    check_combobox.addItem("Item 1")
    check_combobox.addItems(["Item 2", "Item 3"])
    check_combobox.setItemChecked(1, False)
    assert check_combobox.labelText() == "Item 1, Item 3"


def test_paint_event(qtbot: QtBot) -> None:
    """Simple test for paint event; execute without error"""
    check_combobox = QCheckComboBox()
    qtbot.add_widget(check_combobox)
    check_combobox.show()
    check_combobox.setLabelText("A new label")
    check_combobox.paintEvent(QEvent(QEvent.Paint))
    check_combobox.hide()


def test_hidepopup(qtbot: QtBot) -> None:
    check_combobox = QCheckComboBox()
    check_combobox._changed = True
    check_combobox.hidePopup()
    assert check_combobox._changed is False
    check_combobox.hidePopup()


def test_handle_item_checked(qtbot: QtBot) -> None:
    """Tests the check combobox interactions"""
    check_combobox = QCheckComboBox()
    check_combobox.addItems(["Item 1", "Item 2"], [True, False])
    check_combobox.setLabelType(QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS)
    model = check_combobox.model()

    model_index = model.index(0, 0)
    check_combobox._handleItemPressed(model_index)
    assert check_combobox.itemChecked(0) is False

    model_index = model.index(1, 0)
    check_combobox._handleItemPressed(model_index)
    assert check_combobox.itemChecked(1) is True
