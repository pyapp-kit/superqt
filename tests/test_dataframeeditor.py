import pandas as pd
import pytest

from superqt.dataframeeditor import QDataFrameEditor

df = pd.DataFrame({"col1": ["a", "b", "c"], "col2": [1, 3, 2], "col3": [1.3, 2.4, 5.1]})


@pytest.fixture
def dataframe_widget(qtbot):
    def _dataframe_widget(**kwargs):
        widget = QDataFrameEditor(**kwargs)
        widget.show()
        qtbot.addWidget(widget)

        return widget

    return _dataframe_widget


def test_dataframeeditor_defaults(dataframe_widget):
    dataframe_widget()


def test_dataframeeditor_dataframe(dataframe_widget):

    wdg = dataframe_widget()

    wdg._setup_and_check(df)

    assert df.equals(wdg.getValue())

    wdg._dataTable.sortByColumn(1)

    df2 = pd.DataFrame(
        {"col1": ["b", "c", "a"], "col2": [3, 2, 1], "col3": [2.4, 5.1, 1.3]}
    )

    assert df2.values.all() == wdg.getValue().values.all()


def test_dataframeeditor_dataframe_sort(dataframe_widget):

    wdg = dataframe_widget()

    wdg._setup_and_check(df)
    wdg._dataTable.sortByColumn(1)

    df2 = pd.DataFrame(
        {"col1": ["b", "c", "a"], "col2": [3, 2, 1], "col3": [2.4, 5.1, 1.3]}
    )

    assert df2.values.all() == wdg.getValue().values.all()
