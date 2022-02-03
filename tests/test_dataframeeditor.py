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

    wdg = dataframe_widget()
    wdg._setLargeDfSize(25)
    df = pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 3)))
    wdg._setup_and_check(df)


def test_dataframe_bgcolor(dataframe_widget):

    wdg = dataframe_widget()
    df = pd.DataFrame(np.random.choice([20, 30, 40], size=(30, 3)))
    wdg._setup_and_check(df)
    wdg._setLargeDfSize(25)
    wdg._change_bgcolor_enable(1)
