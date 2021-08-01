from enum import Enum

import pytest

from superqt.combobox import EnumComboBox


class Enum1(Enum):
    a = 1
    b = 2
    c = 3


class Enum2(Enum):
    d = 1
    e = 2
    f = 3
    g = 4


class Enum3(Enum):
    a = 1
    b = 2
    c = 3

    def __str__(self):
        return self.name + "1"


class Enum4(Enum):
    a_1 = 1
    b_2 = 2
    c_3 = 3


def test_simple_create(qtbot):
    enum = EnumComboBox(enum_class=Enum1)
    qtbot.addWidget(enum)
    assert enum.count() == 3
    assert [enum.itemText(i) for i in range(enum.count())] == ["a", "b", "c"]


def test_simple_create2(qtbot):
    enum = EnumComboBox()
    qtbot.addWidget(enum)
    assert enum.count() == 0
    enum.setEnumClass(Enum1)
    assert enum.count() == 3
    assert [enum.itemText(i) for i in range(enum.count())] == ["a", "b", "c"]


def test_replace(qtbot):
    enum = EnumComboBox(enum_class=Enum1)
    qtbot.addWidget(enum)
    assert enum.count() == 3
    assert enum.enumClass() == Enum1
    assert isinstance(enum.currentEnum(), Enum1)
    enum.setEnumClass(Enum2)
    assert enum.enumClass() == Enum2
    assert isinstance(enum.currentEnum(), Enum2)
    assert enum.count() == 4
    assert [enum.itemText(i) for i in range(enum.count())] == ["d", "e", "f", "g"]


def test_str_replace(qtbot):
    enum = EnumComboBox(enum_class=Enum3)
    qtbot.addWidget(enum)
    assert enum.count() == 3
    assert [enum.itemText(i) for i in range(enum.count())] == ["a1", "b1", "c1"]


def test_underscore_replace(qtbot):
    enum = EnumComboBox(enum_class=Enum4)
    qtbot.addWidget(enum)
    assert enum.count() == 3
    assert [enum.itemText(i) for i in range(enum.count())] == ["a 1", "b 2", "c 3"]


def test_change_value(qtbot):
    enum = EnumComboBox(enum_class=Enum1)
    qtbot.addWidget(enum)
    assert enum.currentEnum() == Enum1.a
    with qtbot.waitSignal(
        enum.currentEnumChanged, check_params_cb=lambda x: isinstance(x, Enum)
    ):
        enum.setValue(Enum1.c)
    assert enum.currentEnum() == Enum1.c


def test_no_enum(qtbot):
    enum = EnumComboBox()
    assert enum.enumClass() is None
    qtbot.addWidget(enum)
    assert enum.currentEnum() is None


def test_prohibited_methods(qtbot):
    enum = EnumComboBox(enum_class=Enum1)
    qtbot.addWidget(enum)
    with pytest.raises(RuntimeError):
        enum.addItem("aaa")
    with pytest.raises(RuntimeError):
        enum.addItems(["aaa", "bbb"])
    with pytest.raises(RuntimeError):
        enum.insertItem(0, "aaa")
    with pytest.raises(RuntimeError):
        enum.insertItems(0, ["aaa", "bbb"])
    assert enum.count() == 3
