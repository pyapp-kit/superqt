import pytest
from psygnal.containers import SelectableEventedList
from qtpy.QtCore import QModelIndex, Qt

from superqt.listview import QtListModel


class T:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return id(self)

    def __eq__(self, o: object) -> bool:
        return self.name == o


def test_list_model():
    root: SelectableEventedList[str] = SelectableEventedList("abcdef")
    model = QtListModel(root)
    assert all(
        model.data(model.index(i), Qt.UserRole) == letter
        for i, letter in enumerate("abcdef")
    )
    assert all(
        model.data(model.index(i), Qt.DisplayRole) == letter
        for i, letter in enumerate("abcdef")
    )
    # unknown data role
    assert not any(model.data(model.index(i), Qt.FontRole) for i in range(5))
    assert model.flags(QModelIndex()) & Qt.ItemIsDropEnabled
    assert not (model.flags(model.index(1)) & Qt.ItemIsDropEnabled)

    with pytest.raises(TypeError):
        model.setRoot("asdf")

    # smoke test that we can change the root model.
    model.setRoot(SelectableEventedList("zysv"))
