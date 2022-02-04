import numpy as np
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

    df = pd.DataFrame(
        {"col1": ["a", "b", "c"], "col2": [1, 3, 2], "col3": [1.3, 2.4, 5.1]}
    )

    wdg = dataframe_widget()
    wdg._setup_and_check(df)

    assert df.equals(wdg.getValue())

    # test complex number dataframe
    df = pd.DataFrame(
        {"col1": ["a", "b", "c"], "col2": [1j, 3, 2j], "col3": [1.3, 2.4, 5.1]}
    )
    wdg._setup_and_check(df)


def test_dataframeeditor_dataframe_sort(dataframe_widget):

    wdg = dataframe_widget()

    wdg._setup_and_check(df)
    wdg._dataTable.sortByColumn(1)

    df2 = pd.DataFrame(
        {"col1": ["b", "c", "a"], "col2": [3, 2, 1], "col3": [2.4, 5.1, 1.3]}
    )

    assert df2.values.all() == wdg.getValue().values.all()


# QDataFrameModel


def test_qdataframemodel_setData(dataframe_widget):
    wdg = dataframe_widget()
    df = pd.DataFrame(
        {"col1": ["a", "b", "c"], "col2": [1, 3, 2], "col3": [1.3, 2.4, 5.1]}
    )
    wdg._setup_and_check(df)
    index = wdg._model.index(0, 1)
    wdg._model.setData(index, 4)

    df_result = pd.DataFrame(
        {"col1": ["a", "b", "c"], "col2": [4, 3, 2], "col3": [1.3, 2.4, 5.1]}
    )

    assert df_result.equals(wdg.getValue())

    wdg._model.setData(index, "", change_type=bool)
    assert wdg._model.getValue(index.row(), index.column()) is True

    wdg._model.setData(index, 0)
    assert wdg._model.getValue(index.row(), index.column()) is False


def test_dataframe_largedf(dataframe_widget):
    # check that a large dataframe will still load.
    wdg = dataframe_widget()
    wdg._setLargeDfSize(25)
    df = pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 10)))
    wdg._setup_and_check(df)

    wdg._setLargeDfSize(500)
    wdg._setLargeNumRows(20)
    wdg._setLargeNumCols(5)
    wdg._setRowsToLoad(10)
    wdg._setColsToLoad(3)
    wdg._setup_and_check(df)

    assert wdg._model.rowCount() == 10
    assert wdg._model.columnCount() == 3
    assert wdg._model._chunkSize == 30


def test_dataframe_bgcolor(dataframe_widget):

    wdg = dataframe_widget()
    df = pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 3)))
    wdg._enableBackgroundColor(True)
    wdg._setup_and_check(df)

    # empty dataframe
    # test empty dataframe
    df = pd.DataFrame({})
    wdg._setup_and_check(df)

    # test complex with background color
    # test complex number dataframe
    df = pd.DataFrame(
        {"col1": ["a", "b", "c"], "col2": [1j, 3, 2j], "col3": [1.3, 2.4, 5.1]}
    )
    wdg._setup_and_check(df)


def test_dataframe_multiindex(dataframe_widget):

    idx = pd.MultiIndex.from_product([["bar", "baz", "foo", "qux"], ["one", "two"]])
    df = pd.DataFrame(np.random.randn(8, 2), index=idx, columns=["A", "B"])

    wdg = dataframe_widget()
    wdg._enableBackgroundColor(True)
    wdg._setup_and_check(df)


# def test_dataframe_large_rows(dataframe_widget):
#     wdg = dataframe_widget()
#     df = pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 3)))
