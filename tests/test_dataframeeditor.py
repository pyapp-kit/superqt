import numpy as np
import pandas as pd
import pytest

from superqt.dataframeeditor import QDataFrameEditor

idx = pd.MultiIndex.from_product([["bar", "baz", "foo", "qux"], ["one", "two"]])
dataframe = [
    pd.DataFrame({"col1": ["a", "b", "c"], "col2": [1, 3, 2], "col3": [1.3, 2.4, 5.1]}),
    pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 10))),
    pd.DataFrame(
        {
            "col1": ["a", "b", "c"],
            "col2": [complex(0, 1), 3, complex(2, 3)],
            "col3": [1.3, 2.4, 5.1],
        }
    ),
    pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 3))),
    pd.DataFrame(np.random.randn(8, 3), index=idx, columns=["col1", "col2", "col3"]),
]


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


@pytest.mark.parametrize("df", dataframe)
def test_dataframeeditor_dataframe(dataframe_widget, df):

    wdg = dataframe_widget()
    wdg._setup_and_check(df)

    assert df.equals(wdg.getValue())


@pytest.mark.parametrize("df", dataframe)
def test_dataframeeditor_dataframe_sort(dataframe_widget, df):

    wdg = dataframe_widget()

    wdg._setup_and_check(df)
    wdg._dataTable.sortByColumn(1)
    assert wdg._model.getValue(0, 1) == df.max()[1]


@pytest.mark.parametrize("df", dataframe)
def test_qdataframemodel_setData(dataframe_widget, df):

    wdg = dataframe_widget()
    wdg._setup_and_check(df)
    index = wdg._model.index(0, 2)
    wdg._model.setData(index, 4)

    assert wdg._model.getValue(0, 2) == 4


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


@pytest.mark.parametrize("df", dataframe)
def test_dataframe_bgcolor(dataframe_widget, df):

    wdg = dataframe_widget()
    wdg._enableBackgroundColor(True)
    wdg._setup_and_check(df)