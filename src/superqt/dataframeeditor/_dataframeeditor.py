# -----------------------------------------------------------------------------
# Copyright (c) 2011-2012 Lambda Foundry, Inc. and PyData Development Team
# Copyright (c) 2013 Jev Kuznetsov and contributors
# Copyright (c) 2014-2015 Scott Hansen <firecat4153@gmail.com>
# Copyright (c) 2014-2016 Yuri D'Elia "wave++" <wavexx@thregr.org>
# Copyright (c) 2014- Spyder Project Contributors
#
# Components of gtabview originally distributed under the MIT (Expat) license.
# This file as a whole distributed under the terms of the New BSD License
# (BSD 3-clause; see NOTICE.txt in the Spyder root directory for details).
# -----------------------------------------------------------------------------

"""
Pandas DataFrame Editor Dialog.
DataFrameModel is based on the class ArrayModel from array editor
and the class DataFrameModel from the pandas project.
Present in pandas.sandbox.qtpandas in v0.13.1.
DataFrameHeaderModel and DataFrameLevelModel are based on the classes
Header4ExtModel and Level4ExtModel from the gtabview project.
DataFrameModel is based on the classes ExtDataModel and ExtFrameModel, and
DataFrameEditor is based on gtExtTableView from the same project.
DataFrameModel originally based on pandas/sandbox/qtpandas.py of the
`pandas project <https://github.com/pandas-dev/pandas>`_.
The current version is qtpandas/models/DataFrameModel.py of the
`QtPandas project <https://github.com/draperjames/qtpandas>`_.
Components of gtabview from gtabview/viewer.py and gtabview/models.py of the
`gtabview project <https://github.com/TabViewer/gtabview>`_.
"""

# Standard library imports

# Local imports
# from spyder.api.config.mixins import SpyderConfigurationAccessor
# from spyder.config.base import _
# from spyder.config.fonts import DEFAULT_SMALL_DELTA
# from spyder.config.gui import get_font
# from spyder.py3compat import (io, is_text_string, is_type_text_string, PY2,
#                               to_text_string, perf_counter)
from time import perf_counter

import numpy as np

try:
    import pandas as pd
except ImportError:
    raise Exception("To use the dataframeeditor you need to have pandas installed!")

# Third party imports
from qtpy.compat import from_qvariant, to_qvariant
from qtpy.QtCore import (
    QAbstractTableModel,
    QEvent,
    QItemSelectionModel,
    QModelIndex,
    Qt,
    Signal,
)
from qtpy.QtGui import QColor, QCursor
from qtpy.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QItemDelegate,
    QMessageBox,
    QScrollBar,
    QTableView,
    QTableWidget,
    QWidget,
)

# from spyder_kernels.utils.lazymodules import numpy as np, pandas as pd


# from spyder.utils.icon_manager import ima
# from spyder.utils.qthelpers import (add_actions, create_action,
#                                     keybinding, qapplication)
# from spyder.plugins.variableexplorer.widgets.arrayeditor import get_idx_rect
# from spyder.plugins.variableexplorer.widgets.basedialog import BaseDialog

# Supported Numbers and complex numbers
# REAL_NUMBER_TYPES = (float, int, np.int64, np.int32)
# COMPLEX_NUMBER_TYPES = (complex, np.complex64, np.complex128)
# # Used to convert bool intrance to false since bool('False') will return True
# _bool_false = ["false", "f", "0", "0.", "0.0", " "]

# # Default format for data frames with floats
# DEFAULT_FORMAT = "%.6g"

# # Limit at which dataframe is considered so large that it is loaded on demand
# LARGE_SIZE = 5e5
# LARGE_NROWS = 1e5
# LARGE_COLS = 60
# ROWS_TO_LOAD = 500
# COLS_TO_LOAD = 40

# Background colours
# BACKGROUND_NUMBER_MINHUE = 0.66  # hue for largest number
# BACKGROUND_NUMBER_HUERANGE = 0.33  # (hue for smallest) minus (hue for largest)
# BACKGROUND_NUMBER_SATURATION = 0.7
# BACKGROUND_NUMBER_VALUE = 1.0
# BACKGROUND_NUMBER_ALPHA = 0.6
# BACKGROUND_NONNUMBER_COLOR = Qt.lightGray
# # BACKGROUND_INDEX_ALPHA = 0.8
# BACKGROUND_STRING_ALPHA = 0.05
# BACKGROUND_MISC_ALPHA = 0.3


# class BaseDialog(QDialog):
#     def __init__(self, parent=None):
#         QDialog.__init__(self, parent)

#         # # Set style of all QPushButton's inside the dialog.
#         # css = qstylizer.style.StyleSheet()
#         # css.QPushButton.setValues(
#         #     padding='3px 15px 3px 15px',
#         # )
#         # self.setStyleSheet(css.toString())

#     def set_dynamic_width_and_height(
#         self, screen_geometry, width_ratio=0.5, height_ratio=0.5
#     ):
#         """
#     Update width and height using an updated screen geometry.
#     Use a ratio for the width and height of the dialog.
#     """
#     screen_width = int(screen_geometry.width() * width_ratio)
#     screen_height = int(screen_geometry.height() * height_ratio)
#     self.resize(screen_width, screen_height)

#     # Make the dialog window appear in the center of the screen
#     x = int(screen_geometry.center().x() - self.width() / 2)
#     y = int(screen_geometry.center().y() - self.height() / 2)
#     self.move(x, y)

# def show(self):
#     super().show()
#     window = self.window()
#     windowHandle = window.windowHandle()
#     screen = windowHandle.screen()
#     geometry = screen.geometry()
#     self.set_dynamic_width_and_height(geometry)
#     screen.geometryChanged.connect(self.set_dynamic_width_and_height)


def bool_false_check(value, _bool_false):
    """
    Used to convert bool entrance to false.
    Needed since any string in bool('') will return True.
    """
    if value.lower() in _bool_false:
        value = ""
    return value


def global_max(col_vals, index):
    """Returns the global maximum and minimum."""
    col_vals_without_None = [x for x in col_vals if x is not None]
    max_col, min_col = zip(*col_vals_without_None)
    return max(max_col), min(min_col)


class QDataFrameModel(QAbstractTableModel):
    """
    DataFrame Table Model.
    Partly based in ExtDataModel and ExtFrameModel classes
    of the gtabview project.
    For more information please see:
    https://github.com/wavexx/gtabview/blob/master/gtabview/models.py
    """

    def __init__(self, dataFrame, format="%.6g", parent=None):
        QAbstractTableModel.__init__(self)
        self._dialog = parent
        self._df = dataFrame
        self._df_columns_list = None
        self._df_index_list = None
        self._format = format
        self._complex_intran = None
        self._display_error_idxs = []

        self._total_rows = self._df.shape[0]
        self._total_cols = self._df.shape[1]
        size = self._total_rows * self._total_cols

        self._max_min_col = None

        # ppw note: set the ability to color cells from the dataframeeditor
        self._bgcolor_enabled = parent._background_color_enabled
        if parent._background_color_enabled:
            self._max_min_col_update()
            self._colum_avg_enabled = True
            self._bgcolor_enabled = True
            self._column_avg(1)
        else:
            self._colum_avg_enabled = False
            self._bgcolor_enabled = False
            self._column_avg(0)
        # if size < parent._large_df_size:
        #     self._max_min_col_update()
        #     self._colum_avg_enabled = True
        #     # self._bgcolor_enabled = False  # ppw note: turned off for now.
        #     self._column_avg(1)
        # else:
        #     self._colum_avg_enabled = False
        #     # self._bgcolor_enabled = False
        #     self._column_avg(0)

        # Use paging when the total size, number of rows or number of
        # columns is too large
        if size > parent._large_df_size:
            self._rows_loaded = parent._rows_to_load
            self._cols_loaded = parent._cols_to_load
        else:
            if self._total_rows > parent._large_nrows:
                self._rows_loaded = parent._rows_to_load
            else:
                self._rows_loaded = self._total_rows
            if self._total_cols > parent._large_ncols:
                self._cols_loaded = parent._cols_to_load
            else:
                self._cols_loaded = self._total_cols

    def _axis(self, axis):
        """
        Return the corresponding labels taking into account the axis.
        The axis could be horizontal (0) or vertical (1).
        """
        return self._df.columns if axis == 0 else self._df.index

    def _axis_list(self, axis):
        """
        Return the corresponding labels as a list taking into account the axis.
        The axis could be horizontal (0) or vertical (1).
        """
        if axis == 0:
            if self._df_columns_list is None:
                self._df_columns_list = self._df.columns.tolist()
            return self._df_columns_list
        else:
            if self._df_index_list is None:
                self._df_index_list = self._df.index.tolist()
            return self._df_index_list

    def _axis_levels(self, axis):
        """
        Return the number of levels in the labels taking into account the axis.
        Get the number of levels for the columns (0) or rows (1).
        """
        ax = self._axis(axis)
        return 1 if not hasattr(ax, "levels") else len(ax.levels)

    @property
    def shape(self):  # ppw note: should this be private?
        """Return the shape of the dataframe."""
        return self._df.shape

    @property
    def _headerShape(self):
        """Return the levels for the columns and rows of the dataframe."""
        return (self._axis_levels(0), self._axis_levels(1))

    @property
    def _chunkSize(self):
        """Return the max value of the dimensions of the dataframe."""
        return max(*self.shape)

    def _header(self, axis, x, level=0):
        """
        Return the values of the labels for the header of columns or rows.
        The value corresponds to the header of column or row x in the
        given level.
        """
        ax = self._axis(axis)
        if not hasattr(ax, "levels"):
            ax = self._axis_list(axis)
            return ax[x]
        else:
            return ax.values[x][level]

    def _name(self, axis, level):
        """Return the labels of the levels if any."""
        ax = self._axis(axis)
        if hasattr(ax, "levels"):
            return ax.names[level]
        if ax.name:
            return ax.name

    def _max_min_col_update(self):
        """
        Determines the maximum and minimum number in each column.
        The result is a list whose k-th entry is [vmax, vmin], where vmax and
        vmin denote the maximum and minimum of the k-th column (ignoring NaN).
        This list is stored in self.max_min_col.
        If the k-th column has a non-numerical dtype, then the k-th entry
        is set to None. If the dtype is complex, then compute the maximum and
        minimum of the absolute values. If vmax equals vmin, then vmin is
        decreased by one.
        """
        if self._df.shape[0] == 0:  # If no rows to compute max/min then return
            return
        self._max_min_col = []
        for __, col in self._df.iteritems():
            # This is necessary to catch an error in Pandas when computing
            # the maximum of a column.
            # Fixes spyder-ide/spyder#17145
            try:
                if (
                    col.dtype
                    in self._dialog._real_number_types
                    + self._dialog._complex_number_types
                ):
                    if col.dtype in self._dialog._real_number_types:
                        vmax = col.max(skipna=True)
                        vmin = col.min(skipna=True)
                    else:
                        vmax = col.abs().max(skipna=True)
                        vmin = col.abs().min(skipna=True)
                    if vmax != vmin:
                        max_min = [vmax, vmin]
                    else:
                        max_min = [vmax, vmin - 1]
                else:
                    max_min = None
            except TypeError:
                max_min = None
            self._max_min_col.append(max_min)

    def _getFormat(self):
        """Return current format"""
        # Avoid accessing the private attribute _format from outside
        return self._format

    def _setFormat(self, format):
        """Change display format"""
        self._format = format
        self.reset()

    def _bg_color(self, state):
        """Toggle backgroundcolor"""
        self._bgcolor_enabled = state > 0
        self.reset()

    def _column_avg(self, state):
        """Toggle backgroundcolor"""
        self._colum_avg_enabled = state > 0
        if self._colum_avg_enabled:
            self.return_max = lambda col_vals, index: col_vals[index]
        else:
            self.return_max = global_max
        self.reset()

    def _get_bg_color(self, index):
        """Background color depending on value."""
        column = index.column()
        if not self._bgcolor_enabled:
            return
        value = self.getValue(index.row(), column)
        if self._max_min_col[column] is None or pd.isna(value):
            color = QColor(self._dialog._background_nonnumber_color)
            if type(value) == str:  # ppw change
                # if is_text_string(value):
                color.setAlphaF(self._dialog._background_string_alpha)
            else:
                color.setAlphaF(self._dialog._background_misc_alpha)
        else:
            if isinstance(value, self._dialog._complex_number_types):
                color_func = abs
            else:
                color_func = float
            vmax, vmin = self.return_max(self._max_min_col, column)
            if vmax - vmin == 0:
                vmax_vmin_diff = 1.0
            else:
                vmax_vmin_diff = vmax - vmin
            hue = (
                self._dialog._background_number_min_hue
                + self._dialog._background_number_hue_range
                * (vmax - color_func(value))
                / (vmax_vmin_diff)
            )
            hue = float(abs(hue))
            if hue > 1:
                hue = 1
            color = QColor.fromHsvF(
                hue,
                self._dialog._background_number_saturation,
                self._dialog._background_number_value,
                self._dialog._background_number_alpha,
            )
        return color

    def getValue(self, row, column):  # ppw:  should this be private?
        """Return the value of the DataFrame."""
        # To increase the performance iat is used but that requires error
        # handling, so fallback uses iloc
        try:
            value = self._df.iat[row, column]
        except pd._libs.tslib.OutOfBoundsDatetime:
            value = self._df.iloc[:, column].astype(str).iat[row]
        except:  # noqa E722:
            value = self._df.iloc[row, column]
        return value

    def data(self, index, role=Qt.DisplayRole):
        """Cell content"""
        if not index.isValid():
            return to_qvariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            row = index.row()
            value = self.getValue(row, column)
            if isinstance(value, float):
                try:
                    return to_qvariant(self._format % value)
                except (ValueError, TypeError):
                    # may happen if format = '%d' and value = NaN;
                    # see spyder-ide/spyder#4139.
                    return to_qvariant(self._dialog._default_format % value)
            elif type(value) == str:  # ppw change
                # elif is_type_text_string(value):
                # Don't perform any conversion on strings
                # because it leads to differences between
                # the data present in the dataframe and
                # what is shown by Spyder
                return value
            else:
                try:
                    return to_qvariant(str(value))
                    # return to_qvariant(to_text_string(value))
                except Exception:
                    self._display_error_idxs.append(index)
                    return "Display Error!"
        elif role == Qt.BackgroundColorRole:
            return to_qvariant(self._get_bg_color(index))
        # elif role == Qt.FontRole:
        #     return to_qvariant(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
        elif role == Qt.ToolTipRole:
            if index in self._display_error_idxs:
                return (
                    "It is not possible to display this value because\n"
                    "an error ocurred while trying to do it"
                )
        return to_qvariant()

    def _recalculateIndex(self):
        """Recalcuate index information."""
        self._df_index_list = self._df.index.tolist()

    def sort(self, column, order=Qt.AscendingOrder):
        """Overriding sort method"""
        if self._complex_intran is not None:
            if self._complex_intran.any(axis=0).iloc[column]:
                QMessageBox.critical(
                    self._dialog,
                    "Error",
                    "TypeError error: no ordering "
                    "relation is defined for complex numbers",
                )
                return False
        try:
            ascending = order == Qt.AscendingOrder
            if column >= 0:
                try:
                    self._df.sort_values(
                        by=self._df.columns[column],
                        ascending=ascending,
                        inplace=True,
                        kind="mergesort",
                    )
                except AttributeError:
                    # for pandas version < 0.17
                    self._df.sort(
                        columns=self._df.columns[column],
                        ascending=ascending,
                        inplace=True,
                        kind="mergesort",
                    )
                except ValueError as e:
                    # Not possible to sort on duplicate columns
                    # See spyder-ide/spyder#5225.
                    QMessageBox.critical(
                        self._dialog, "Error", "ValueError: %s" % str(e)
                    )
                    #  "ValueError: %s" % to_text_string(e))
                except SystemError as e:
                    # Not possible to sort on category dtypes
                    # See spyder-ide/spyder#5361.
                    QMessageBox.critical(
                        self._dialog, "Error", "SystemError: %s" % str(e)
                    )
                    #  "SystemError: %s" % to_text_string(e))
            else:
                # Update index list
                self._recalculateIndex()
                # To sort by index
                self._df.sort_index(inplace=True, ascending=ascending)
        except TypeError as e:
            QMessageBox.critical(self._dialog, "Error", "TypeError error: %s" % str(e))
            #  "TypeError error: %s" % to_text_string(e))
            return False

        self.reset()
        return True

    def flags(self, index):
        """Set flags"""
        return Qt.ItemFlags(
            int(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        )

    def setData(self, index, value, role=Qt.EditRole, change_type=None):
        """Cell content change

        Parameters
        -----------
        change_type: function that converts the data in cells (ex. float, str, bool, etc)

        """
        column = index.column()
        row = index.row()
        if index in self._display_error_idxs:
            return False
        if change_type is not None:
            try:
                # ppw note: from what I can see, the intent of this block of code is not to set a new
                # value and change the type.  For example, if you want to set a value to
                # False and change from int to bool, this will not currently work.  It appears
                # the original intent of this block was to be set via a menu where you change
                # the type, then you can edit the values separately.
                value = self.data(index, role=Qt.DisplayRole)
                val = from_qvariant(value, str)
                if change_type is bool:
                    val = bool_false_check(val, self._dialog._bool_false)
                self._df.iloc[row, column] = change_type(val)
            except ValueError:
                self._df.iloc[row, column] = change_type("0")
        else:
            val = from_qvariant(value, str)
            # ppw note:  this should change to str, but it doesn't yet, so doing this below
            val = str(val)
            current_value = self.getValue(row, column)
            if isinstance(current_value, (bool, np.bool_)):
                val = bool_false_check(val, self._dialog._bool_false)
            supported_types = (bool, np.bool_) + self._dialog._real_number_types
            if (
                isinstance(current_value, supported_types) or type(current_value) == str
            ):  # ppw change
                # is_text_string(current_value)):
                try:
                    self._df.iloc[row, column] = current_value.__class__(val)
                except (ValueError, OverflowError) as e:
                    QMessageBox.critical(
                        self._dialog, "Error", str(type(e).__name__) + ": " + str(e)
                    )
                    return False
            else:
                QMessageBox.critical(
                    self._dialog,
                    "Error",
                    "Editing dtype {!s} not yet supported.".format(
                        type(current_value).__name__
                    ),
                )
                return False
        self._max_min_col_update()
        self.dataChanged.emit(index, index)
        return True

    def getData(self):  # ppw: not sure if this is Qt method.
        """Return data"""
        return self._df

    def rowCount(self, index=QModelIndex()):
        """DataFrame row number"""
        # Avoid a "Qt exception in virtual methods" generated in our
        # tests on Windows/Python 3.7
        # See spyder-ide/spyder#8910.
        try:
            if self._total_rows <= self._rows_loaded:
                return self._total_rows
            else:
                return self._rows_loaded
        except AttributeError:
            return 0

    def _fetch_more(self, rows=False, columns=False):
        """Get more columns and/or rows."""
        if rows and self._total_rows > self._rows_loaded:
            reminder = self._total_rows - self._rows_loaded
            items_to_fetch = min(reminder, self._rows_to_load)
            self.beginInsertRows(
                QModelIndex(), self._rows_loaded, self._rows_loaded + items_to_fetch - 1
            )
            self._rows_loaded += items_to_fetch
            self.endInsertRows()
        if columns and self._total_cols > self._cols_loaded:
            reminder = self._total_cols - self._cols_loaded
            items_to_fetch = min(reminder, self._cols_to_load)
            self.beginInsertColumns(
                QModelIndex(), self._cols_loaded, self._cols_loaded + items_to_fetch - 1
            )
            self._cols_loaded += items_to_fetch
            self.endInsertColumns()

    def columnCount(self, index=QModelIndex()):
        """DataFrame column number"""
        # Avoid a "Qt exception in virtual methods" generated in our
        # tests on Windows/Python 3.7
        # See spyder-ide/spyder#8910.
        try:
            # This is done to implement series
            if len(self._df.shape) == 1:
                return 2
            elif self._total_cols <= self._cols_loaded:
                return self._total_cols
            else:
                return self._cols_loaded
        except AttributeError:
            return 0

    def reset(self):
        self.beginResetModel()
        self.endResetModel()


class DataFrameView(QTableView):
    # class DataFrameView(QTableView, SpyderConfigurationAccessor):
    """
    Data Frame view class.
    Signals
    -------
    sig_sort_by_column(): Raised after more columns are fetched.
    sig_fetch_more_rows(): Raised after more rows are fetched.
    """
    sig_sort_by_column = Signal()
    sig_fetch_more_columns = Signal()
    sig_fetch_more_rows = Signal()

    # CONF_SECTION = "variable_explorer"

    def __init__(self, parent, model, header, hscroll, vscroll):
        """Constructor."""
        QTableView.__init__(self, parent)
        self.setModel(model)
        self.setHorizontalScrollBar(hscroll)
        self.setVerticalScrollBar(vscroll)

        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)

        self._sort_old = [None]
        self._header_class = header
        self._header_class.sectionClicked.connect(self.sortByColumn)
        # self.menu = self.setup_menu()
        # self.config_shortcut(self.copy, 'copy', self)
        self.horizontalScrollBar().valueChanged.connect(self._load_more_columns)
        self.verticalScrollBar().valueChanged.connect(self._load_more_rows)

    def _load_more_columns(self, value):
        """Load more columns to display."""
        # Needed to avoid a NameError while fetching data when closing
        # See spyder-ide/spyder#12034.
        try:
            self._load_more_data(value, columns=True)
        except NameError:
            pass

    def _load_more_rows(self, value):
        """Load more rows to display."""
        # Needed to avoid a NameError while fetching data when closing
        # See spyder-ide/spyder#12034.
        try:
            self._load_more_data(value, rows=True)
        except NameError:
            pass

    def _load_more_data(self, value, rows=False, columns=False):
        """Load more rows and columns to display."""
        try:
            if rows and value == self.verticalScrollBar().maximum():
                self.model()._fetch_more(rows=rows)
                self.sig_fetch_more_rows.emit()
            if columns and value == self.horizontalScrollBar().maximum():
                self.model()._fetch_more(columns=columns)
                self.sig_fetch_more_columns.emit()

        except NameError:
            # Needed to handle a NameError while fetching data when closing
            # See spyder-ide/spyder#7880.
            pass

    def sortByColumn(self, index):
        """Implement a column sort."""
        if self._sort_old == [None]:
            self._header_class.setSortIndicatorShown(True)
        sort_order = self._header_class.sortIndicatorOrder()
        if not self.model().sort(index, sort_order):
            if len(self._sort_old) != 2:
                self._header_class.setSortIndicatorShown(False)
            else:
                self._header_class.setSortIndicator(
                    self._sort_old[0], self._sort_old[1]
                )
            return
        self._sort_old = [index, self._header_class.sortIndicatorOrder()]
        self.sig_sort_by_column.emit()

    #     def contextMenuEvent(self, event):
    #         """Reimplement Qt method."""
    #         self.menu.popup(event.globalPos())
    #         event.accept()

    #     def setup_menu(self):
    #         """Setup context menu."""
    #         copy_action = create_action(self, _('Copy'),
    #                                     shortcut=keybinding('Copy'),
    #                                     icon=ima.icon('editcopy'),
    #                                     triggered=self.copy,
    #                                     context=Qt.WidgetShortcut)
    #         functions = ((_("To bool"), bool), (_("To complex"), complex),
    #                      (_("To int"), int), (_("To float"), float),
    #                      (_("To str"), to_text_string))
    #         types_in_menu = [copy_action]
    #         for name, func in functions:
    #             def slot():
    #                 self._change_type(func)
    #             types_in_menu += [create_action(self, name,
    #                                             triggered=slot,
    #                                             context=Qt.WidgetShortcut)]
    #         menu = QMenu(self)
    #         add_actions(menu, types_in_menu)
    #         return menu

    def _change_type(self, func):
        """A function that changes types of cells."""
        model = self.model()
        index_list = self.selectedIndexes()
        [model.setData(i, "", change_type=func) for i in index_list]


#     @Slot()
#     def copy(self):
#         """Copy text to clipboard"""
#         if not self.selectedIndexes():
#             return
#         (row_min, row_max,
#          col_min, col_max) = get_idx_rect(self.selectedIndexes())
#         # Copy index and header too (equal True).
#         # See spyder-ide/spyder#11096
#         index = header = True
#         df = self.model()._df
#         obj = df.iloc[slice(row_min, row_max + 1),
#                       slice(col_min, col_max + 1)]
#         output = io.StringIO()
#         try:
#             obj.to_csv(output, sep='\t', index=index, header=header)
#         except UnicodeEncodeError:
#             # Needed to handle encoding errors in Python 2
#             # See spyder-ide/spyder#4833
#             QMessageBox.critical(
#                 self,
#                 _("Error"),
#                 _("Text can't be copied."))
#         if not PY2:
#             contents = output.getvalue()
#         else:
#             contents = output.getvalue().decode('utf-8')
#         output.close()
#         clipboard = QApplication.clipboard()
#         clipboard.setText(contents)


class DataFrameHeaderModel(QAbstractTableModel):
    """
    This class is the model for the header or index of the DataFrameEditor.
    Taken from gtabview project (Header4ExtModel).
    For more information please see:
    https://github.com/wavexx/gtabview/blob/master/gtabview/viewer.py
    """

    COLUMN_INDEX = -1  # Makes reference to the index of the table.

    def __init__(self, model, axis, palette):
        """
        Header constructor.
        The 'model' is the QAbstractTableModel of the dataframe, the 'axis' is
        to acknowledge if is for the header (horizontal - 0) or for the
        index (vertical - 1) and the palette is the set of colors to use.
        """
        super().__init__()
        self._model = model
        self._axis = axis
        self._palette = palette
        self._total_rows = self._model.shape[0]
        self._total_cols = self._model.shape[1]
        size = self._total_rows * self._total_cols

        # Use paging when the total size, number of rows or number of
        # columns is too large
        if size > self._model._dialog._large_df_size:
            self._rows_loaded = self._model._dialog._rows_to_load
            self._cols_loaded = self._model._dialog._cols_to_load
        else:
            if self._total_cols > self._model._dialog._large_ncols:
                self._cols_loaded = self._model._dialog._cols_to_load
            else:
                self._cols_loaded = self._total_cols
            if self._total_rows > self._model._dialog._large_nrows:
                self._rows_loaded = self._model._dialog._rows_to_load
            else:
                self._rows_loaded = self._total_rows

        if self._axis == 0:
            self._total_cols = self._model.shape[1]
            self._shape = (self._model._headerShape[0], self._model.shape[1])
        else:
            self._total_rows = self._model.shape[0]
            self._shape = (self._model.shape[0], self._model._headerShape[1])

    def rowCount(self, index=None):
        """Get number of rows in the header."""
        if self._axis == 0:
            return max(1, self._shape[0])
        else:
            if self._total_rows <= self._rows_loaded:
                return self._total_rows
            else:
                return self._rows_loaded

    def columnCount(self, index=QModelIndex()):
        """DataFrame column number"""
        if self._axis == 0:
            if self._total_cols <= self._cols_loaded:
                return self._total_cols
            else:
                return self._cols_loaded
        else:
            return max(1, self._shape[1])

    def _fetch_more(self, rows=False, columns=False):
        """Get more columns or rows (based on axis)."""
        if self._axis == 1 and self._total_rows > self._rows_loaded:
            reminder = self._total_rows - self._rows_loaded
            items_to_fetch = min(reminder, self._rows_to_load)
            self.beginInsertRows(
                QModelIndex(), self._rows_loaded, self._rows_loaded + items_to_fetch - 1
            )
            self._rows_loaded += items_to_fetch
            self.endInsertRows()
        if self._axis == 0 and self._total_cols > self._cols_loaded:
            reminder = self._total_cols - self._cols_loaded
            items_to_fetch = min(reminder, self._cols_to_load)
            self.beginInsertColumns(
                QModelIndex(), self._cols_loaded, self._cols_loaded + items_to_fetch - 1
            )
            self._cols_loaded += items_to_fetch
            self.endInsertColumns()

    def sort(self, column, order=Qt.AscendingOrder):
        """Overriding sort method."""
        ascending = order == Qt.AscendingOrder
        self._model.sort(self.COLUMN_INDEX, order=ascending)
        return True

    def headerData(self, section, orientation, role):
        """Get the information to put in the header."""
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignCenter
            else:
                return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.DisplayRole and role != Qt.ToolTipRole:
            return None
        if self._axis == 1 and self._shape[1] <= 1:
            return None
        orient_axis = 0 if orientation == Qt.Horizontal else 1
        if self._model._headerShape[orient_axis] > 1:
            header = section
        else:
            header = self._model._header(self._axis, section)

            # Don't perform any conversion on strings
            # because it leads to differences between
            # the data present in the dataframe and
            # what is shown by Spyder
            # if not is_type_text_string(header):
            #     header = to_text_string(header)

        return header

    def data(self, index, role):
        """
        Get the data for the header.
        This is used when a header has levels.
        """
        if (
            not index.isValid()
            or index.row() >= self._shape[0]
            or index.column() >= self._shape[1]
        ):
            return None
        row, col = (
            (index.row(), index.column())
            if self._axis == 0
            else (index.column(), index.row())
        )
        if role != Qt.DisplayRole:
            return None
        if self._axis == 0 and self._shape[0] <= 1:
            return None

        header = self._model._header(self._axis, col, row)

        # Don't perform any conversion on strings
        # because it leads to differences between
        # the data present in the dataframe and
        # what is shown by Spyder
        # if not is_type_text_string(header):
        #     header = to_text_string(header)

        return header


class DataFrameLevelModel(QAbstractTableModel):
    """
    Data Frame level class.
    This class is used to represent index levels in the DataFrameEditor. When
    using MultiIndex, this model creates labels for the index/header as Index i
    for each section in the index/header
    Based on the gtabview project (Level4ExtModel).
    For more information please see:
    https://github.com/wavexx/gtabview/blob/master/gtabview/viewer.py
    """

    def __init__(self, model, palette, font):
        super().__init__()
        self._model = model
        self._background = palette.dark().color()
        if self._background.lightness() > 127:
            self._foreground = palette.text()
        else:
            self._foreground = palette.highlightedText()
        self._palette = palette
        font.setBold(True)
        self._font = font

    def rowCount(self, index=None):
        """Get number of rows (number of levels for the header)."""
        return max(1, self._model._headerShape[0])

    def columnCount(self, index=None):
        """Get the number of columns (number of levels for the index)."""
        return max(1, self._model._headerShape[1])

    def headerData(self, section, orientation, role):
        """
        Get the text to put in the header of the levels of the indexes.
        By default it returns 'Index i', where i is the section in the index
        """
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return Qt.AlignCenter
            else:
                return Qt.AlignRight | Qt.AlignVCenter
        if role != Qt.DisplayRole and role != Qt.ToolTipRole:
            return None
        if self._model._headerShape[0] <= 1 and orientation == Qt.Horizontal:
            if self._model._name(1, section):
                return self._model._name(1, section)
            return "Index"
        elif self._model._headerShape[0] <= 1:
            return None
        elif self._model._headerShape[1] <= 1 and orientation == Qt.Vertical:
            return None
        return "Index" + " " + str(section)
        # return 'Index' + ' ' + to_text_string(section)

    def data(self, index, role):
        """Get the information of the levels."""
        if not index.isValid():
            return None
        if role == Qt.FontRole:
            return self._font
        label = ""
        if index.column() == self._model._headerShape[1] - 1:
            label = str(self._model._name(0, index.row()))
        elif index.row() == self._model._headerShape[0] - 1:
            label = str(self._model._name(1, index.column()))
        if role == Qt.DisplayRole and label:
            return label
        elif role == Qt.ForegroundRole:
            return self._foreground
        elif role == Qt.BackgroundRole:
            return self._background
        elif role == Qt.BackgroundRole:
            return self._palette.window()
        return None


class QDataFrameEditor(QWidget):
    # class DataFrameEditor(BaseDialog, SpyderConfigurationAccessor):
    """
    Widget for displaying and editing DataFrame and related objects.
    Based on the gtabview project (ExtTableView).
    For more information please see:
    https://github.com/wavexx/gtabview/blob/master/gtabview/viewer.py
    """
    # CONF_SECTION = "variable_explorer"

    def __init__(self, parent=None):
        super().__init__(parent)

        # Destroying the C++ object right after closing the dialog box,
        # otherwise it may be garbage-collected in another QThread
        # (e.g. the editor's analysis thread in Spyder), thus leading to
        # a segmentation fault on UNIX or an application crash on Windows
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._is_series = False
        # self.layout = None

        self._real_number_types = (float, int, np.int64, np.int32)
        self._complex_number_types = (complex, np.complex64, np.complex128)
        # Used to convert bool intrance to false since bool('False') will return True
        self._bool_false = ["false", "f", "0", "0.", "0.0", " "]

        # Default format for data frames with floats
        self._default_format = "%.6g"

        # Limit at which dataframe is considered so large that it is loaded on demand
        self._large_df_size = 5e5  # LARGE_SIZE
        self._large_nrows = 1e5  # LARGE_NROWS
        self._large_ncols = 60  # LARGE_COLS
        self._rows_to_load = 500  # ROWS_TO_LOAD
        self._cols_to_load = 40  # COLS_TO_LOAD

        # Background colours
        self._background_color_enabled = False
        self._background_number_min_hue = (
            0.66  # hue for largest number  BACKGROUND_NUMBER_MINHUE
        )
        self._background_number_hue_range = 0.33  # (hue for smallest) minus (hue for largest) BACKGROUND_NUMBER_HUERANGE
        self._background_number_saturation = 0.7  # BACKGROUND_NUMBER_SATURATION
        self._background_number_value = 1.0  # BACKGROUND_NUMBER_VALUE
        self._background_number_alpha = 0.6  # BACKGROUND_NUMBER_ALPHA
        self._background_nonnumber_color = Qt.lightGray  # BACKGROUND_NONNUMBER_COLOR
        # self._background_index_alpha = 0.8   # BACKGROUND_INDEX_ALPHA  not used anywhere?
        self._background_string_alpha = 0.05  # BACKGROUND_STRING_ALPHA
        self._background_misc_alpha = 0.3  # BACKGROUND_MISC_ALPHA

        # self.setWindowTitle(title)

    def _setup_and_check(self, data):
        """
        Setup DataFrameEditor:
        return False if data is not supported, True otherwise.
        Supported types for data are DataFrame, Series and Index.
        """
        # self._selection_rec = False
        self._model = None

        self._layout = QGridLayout()
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(20, 20, 20, 0)
        self.setLayout(self._layout)
        #         if title:
        #             title = to_text_string(title) + " - %s" % data.__class__.__name__
        #         else:
        #             title = _("%s editor") % data.__class__.__name__

        if isinstance(data, pd.Series):
            self._is_series = True
            data = data.to_frame()
        elif isinstance(data, pd.Index):
            data = pd.DataFrame(data)

        self._hscroll = QScrollBar(Qt.Horizontal)
        self._vscroll = QScrollBar(Qt.Vertical)

        # Create the view for the level
        self._create_table_level()

        # Create the view for the horizontal header
        self._create_table_header()

        # Create the view for the vertical index
        self._create_table_index()

        # Create the model and view of the data
        self._dataModel = QDataFrameModel(data, parent=self)
        # self._dataModel.dataChanged.connect(self._save_and_close_enable)
        self._create_data_table()

        self._layout.addWidget(self._hscroll, 2, 0, 1, 2)
        self._layout.addWidget(self._vscroll, 0, 2, 2, 1)

        # autosize columns on-demand
        self._autosized_cols = set()
        # Set limit time to calculate column sizeHint to 300ms,
        # See spyder-ide/spyder#11060
        self._max_autosize_ms = 300
        self._dataTable.installEventFilter(self)

        avg_width = self.fontMetrics().averageCharWidth()
        self._min_trunc = avg_width * 12  # Minimum size for columns
        self._max_width = avg_width * 64  # Maximum size for columns

        self.setLayout(self._layout)
        # Make the dialog act as a window
        # self.setWindowFlags(Qt.Window)
        # btn_layout = QHBoxLayout()
        # btn_layout.setSpacing(5)

        # btn_format = QPushButton("Format")
        # disable format button for int type
        # btn_layout.addWidget(btn_format)
        # btn_format.clicked.connect(self.change_format)

        # btn_resize = QPushButton("Resize")
        # btn_layout.addWidget(btn_resize)
        # btn_resize.clicked.connect(self._resize_to_contents)

        # bgcolor = QCheckBox("Background color")
        # bgcolor.setChecked(self._dataModel._bgcolor_enabled)
        # bgcolor.setEnabled(self._dataModel._bgcolor_enabled)
        # bgcolor.stateChanged.connect(self._change_bgcolor_enable)
        # btn_layout.addWidget(bgcolor)

        # self.bgcolor_global = QCheckBox("Column min/max")
        # self.bgcolor_global.setChecked(self._dataModel._colum_avg_enabled)
        # self.bgcolor_global.setEnabled(
        # not self._is_series and self._dataModel._bgcolor_enabled
        # )
        # self.bgcolor_global.stateChanged.connect(self._dataModel.colum_avg)
        # btn_layout.addWidget(self.bgcolor_global)

        # btn_layout.addStretch()

        # self.btn_save_and_close = QPushButton("Save and Close")
        # self.btn_save_and_close.setDisabled(True)
        # self.btn_save_and_close.clicked.connect(self.accept)
        # btn_layout.addWidget(self.btn_save_and_close)

        # self.btn_close = QPushButton("Close")
        # self.btn_close.setAutoDefault(True)
        # self.btn_close.setDefault(True)
        # self.btn_close.clicked.connect(self.reject)
        # btn_layout.addWidget(self.btn_close)

        # btn_layout.setContentsMargins(0, 16, 0, 16)
        # self._layout.addLayout(btn_layout, 4, 0, 1, 2)
        self.setModel(self._dataModel)
        self.resizeColumnsToContents()

        #         format = '%' + self.get_conf('dataframe_format')
        #         self._dataModel._setFormat(format)

        return True

    # @Slot(QModelIndex, QModelIndex)
    # def _save_and_close_enable(self, top_left, bottom_right):
    #     """Handle the data change event to enable the save and close button."""
    #     self.btn_save_and_close.setEnabled(True)
    #     self.btn_save_and_close.setAutoDefault(True)
    #     self.btn_save_and_close.setDefault(True)

    def _create_table_level(self):
        """Create the QTableView that will hold the level model."""
        self._table_level = QTableView()
        self._table_level.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table_level.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_level.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_level.setFrameStyle(QFrame.Plain)
        self._table_level.horizontalHeader().sectionResized.connect(self._index_resized)
        self._table_level.verticalHeader().sectionResized.connect(self._header_resized)
        self._table_level.setItemDelegate(QItemDelegate())
        self._layout.addWidget(self._table_level, 0, 0)
        self._table_level.setContentsMargins(0, 0, 0, 0)
        self._table_level.horizontalHeader().sectionClicked.connect(self._sortByIndex)

    def _create_table_header(self):
        """Create the QTableView that will hold the header model."""
        self._table_header = QTableView()
        self._table_header.verticalHeader().hide()
        self._table_header.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table_header.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_header.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_header.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self._table_header.setHorizontalScrollBar(self._hscroll)
        self._table_header.setFrameStyle(QFrame.Plain)
        self._table_header.horizontalHeader().sectionResized.connect(
            self._column_resized
        )
        self._table_header.setItemDelegate(QItemDelegate())
        self._layout.addWidget(self._table_header, 0, 1)

    def _create_table_index(self):
        """Create the QTableView that will hold the index model."""
        self._table_index = QTableView()
        self._table_index.horizontalHeader().hide()
        self._table_index.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table_index.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_index.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._table_index.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self._table_index.setVerticalScrollBar(self._vscroll)
        self._table_index.setFrameStyle(QFrame.Plain)
        self._table_index.verticalHeader().sectionResized.connect(self._row_resized)
        self._table_index.setItemDelegate(QItemDelegate())
        self._layout.addWidget(self._table_index, 1, 0)
        self._table_index.setContentsMargins(0, 0, 0, 0)

    def _create_data_table(self):
        """Create the QTableView that will hold the data model."""
        self._dataTable = DataFrameView(
            self,
            self._dataModel,
            self._table_header.horizontalHeader(),
            self._hscroll,
            self._vscroll,
        )
        self._dataTable.verticalHeader().hide()
        self._dataTable.horizontalHeader().hide()
        self._dataTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._dataTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._dataTable.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        self._dataTable.setVerticalScrollMode(QTableView.ScrollPerPixel)
        self._dataTable.setFrameStyle(QFrame.Plain)
        self._dataTable.setItemDelegate(QItemDelegate())
        self._layout.addWidget(self._dataTable, 1, 1)
        self.setFocusProxy(self._dataTable)
        self._dataTable.sig_sort_by_column.connect(self._sort_update)
        self._dataTable.sig_fetch_more_columns.connect(self._fetch_more_columns)
        self._dataTable.sig_fetch_more_rows.connect(self._fetch_more_rows)

    def _sortByIndex(self, index):  # ppw?  is this a QT method?  should it be public?
        """Implement a Index sort."""
        self._table_level.horizontalHeader().setSortIndicatorShown(True)
        sort_order = self._table_level.horizontalHeader().sortIndicatorOrder()
        self._table_index.model().sort(index, sort_order)
        self._sort_update()

    def model(self):
        """Get the model of the dataframe."""
        return self._model

    def _setLargeDfSize(self, value):
        self._large_df_size = value

    def _setLargeNumRows(self, value):
        self._large_nrows = value

    def _setLargeNumCols(self, value):
        self._large_ncols = value

    def _setRowsToLoad(self, value):
        self._rows_to_load = value

    def _setColsToLoad(self, value):
        self._cols_to_load = value

    def _enableBackgroundColor(self, value):
        self._background_color_enabled = value

    def _setBackgroundNumMinHue(self, value):
        self._background_number_min_hue = value

    def _setBackgroundNumHueRange(self, value):
        # (hue for smallest) minus (hue for largest)
        self._background_number_hue_range = value

    def _setBackgroundNumSaturation(self, value):
        self._background_number_saturation = value

    def _setBackgroundNumValue(self, value):
        self._background_number_value = value

    def _setBackgroundNumAlpha(self, value):
        self._background_number_alpha = value

    def _setBackgroundNonNumberColor(self, value):
        self._background_nonnumber_color = Qt.lightGray

    # def setBackgroundIndexAlpha(self, value):
    #     self._background_index_alpha = value

    def _setBackgroundStringAlpha(self, value):
        self._background_string_alpha = value

    def _setBackgroundMiscAlpha(self, value):
        self._background_misc_alpha = value

    def _column_resized(self, col, old_width, new_width):
        """Update the column width."""
        self._dataTable.setColumnWidth(col, new_width)
        self._update_layout()

    def _row_resized(self, row, old_height, new_height):
        """Update the row height."""
        self._dataTable.setRowHeight(row, new_height)
        self._update_layout()

    def _index_resized(self, col, old_width, new_width):
        """Resize the corresponding column of the index section selected."""
        self._table_index.setColumnWidth(col, new_width)
        self._update_layout()

    def _header_resized(self, row, old_height, new_height):
        """Resize the corresponding row of the header section selected."""
        self._table_header.setRowHeight(row, new_height)
        self._update_layout()

    def _update_layout(self):
        """Set the width and height of the QTableViews and hide rows."""
        h_width = max(
            self._table_level.verticalHeader().sizeHint().width(),
            self._table_index.verticalHeader().sizeHint().width(),
        )
        self._table_level.verticalHeader().setFixedWidth(h_width)
        self._table_index.verticalHeader().setFixedWidth(h_width)

        last_row = self._model._headerShape[0] - 1
        if last_row < 0:
            hdr_height = self._table_level.horizontalHeader().height()
        else:
            hdr_height = (
                self._table_level.rowViewportPosition(last_row)
                + self._table_level.rowHeight(last_row)
                + self._table_level.horizontalHeader().height()
            )
            # Check if the header shape has only one row (which display the
            # same info than the horizontal header).
            if last_row == 0:
                self._table_level.setRowHidden(0, True)
                self._table_header.setRowHidden(0, True)
        self._table_header.setFixedHeight(hdr_height)
        self._table_level.setFixedHeight(hdr_height)

        last_col = self._model._headerShape[1] - 1
        if last_col < 0:
            idx_width = self._table_level.verticalHeader().width()
        else:
            idx_width = (
                self._table_level.columnViewportPosition(last_col)
                + self._table_level.columnWidth(last_col)
                + self._table_level.verticalHeader().width()
            )
        self._table_index.setFixedWidth(idx_width)
        self._table_level.setFixedWidth(idx_width)
        self._resizeVisibleColumnsToContents()

    def _reset_model(self, table, model):
        """Set the model in the given table."""
        old_sel_model = table.selectionModel()
        table.setModel(model)
        if old_sel_model:
            del old_sel_model

    def setAutosizeLimitTime(
        self, limit_ms
    ):  # is this a Qt method anywhere?  make private?
        """Set maximum time to calculate size hint for columns."""
        self._max_autosize_ms = limit_ms

    def setModel(self, model, relayout=True):
        """Set the model for the data, header/index and level views."""
        self._model = model
        sel_model = self._dataTable.selectionModel()
        sel_model.currentColumnChanged.connect(self._resizeCurrentColumnToContents)

        # Asociate the models (level, vertical index and horizontal header)
        # with its corresponding view.
        self._reset_model(
            self._table_level, DataFrameLevelModel(model, self.palette(), self.font())
        )
        self._reset_model(
            self._table_header, DataFrameHeaderModel(model, 0, self.palette())
        )
        self._reset_model(
            self._table_index, DataFrameHeaderModel(model, 1, self.palette())
        )

        # Needs to be called after setting all table models
        if relayout:
            self._update_layout()

    def setCurrentIndex(self, y, x):
        """Set current selection."""
        self._dataTable.selectionModel().setCurrentIndex(
            self._dataTable.model().index(y, x), QItemSelectionModel.ClearAndSelect
        )

    def _sizeHintForColumn(self, table, col, limit_ms=None):
        """Get the size hint for a given column in a table."""
        max_row = table.model().rowCount()
        lm_start = perf_counter()
        lm_row = 64 if limit_ms else max_row
        max_width = self._min_trunc
        for row in range(max_row):
            v = table.sizeHintForIndex(table.model().index(row, col))
            max_width = max(max_width, v.width())
            if row > lm_row:
                lm_now = perf_counter()
                lm_elapsed = (lm_now - lm_start) * 1000
                if lm_elapsed >= limit_ms:
                    break
                lm_row = int((row / lm_elapsed) * limit_ms)
        return max_width

    def _resizeColumnToContents(self, header, data, col, limit_ms):
        """Resize a column by its contents."""
        hdr_width = self._sizeHintForColumn(header, col, limit_ms)
        data_width = self._sizeHintForColumn(data, col, limit_ms)
        if data_width > hdr_width:
            width = min(self._max_width, data_width)
        elif hdr_width > data_width * 2:
            width = max(
                min(hdr_width, self._min_trunc), min(self._max_width, data_width)
            )
        else:
            width = max(min(self._max_width, hdr_width), self._min_trunc)
        header.setColumnWidth(col, width)

    def _resizeColumnsToContents(self, header, data, limit_ms):
        """Resize all the colummns to its contents."""
        max_col = data.model().columnCount()
        if limit_ms is None:
            max_col_ms = None
        else:
            max_col_ms = limit_ms / max(1, max_col)
        for col in range(max_col):
            self._resizeColumnToContents(header, data, col, max_col_ms)

    def eventFilter(self, obj, event):
        """Override eventFilter to catch resize event."""
        if obj == self._dataTable and event.type() == QEvent.Resize:
            self._resizeVisibleColumnsToContents()
        return False

    def _resizeVisibleColumnsToContents(self):
        """Resize the columns that are in the view."""
        index_column = self._dataTable.rect().topLeft().x()
        start = col = self._dataTable.columnAt(index_column)
        width = self._model.shape[1]
        end = self._dataTable.columnAt(self._dataTable.rect().bottomRight().x())
        end = width if end == -1 else end + 1
        if self._max_autosize_ms is None:
            max_col_ms = None
        else:
            max_col_ms = self._max_autosize_ms / max(1, end - start)
        while col < end:
            resized = False
            if col not in self._autosized_cols:
                self._autosized_cols.add(col)
                resized = True
                self._resizeColumnToContents(
                    self._table_header, self._dataTable, col, max_col_ms
                )
            col += 1
            if resized:
                # As we resize columns, the boundary will change
                index_column = self._dataTable.rect().bottomRight().x()
                end = self._dataTable.columnAt(index_column)
                end = width if end == -1 else end + 1
                if max_col_ms is not None:
                    max_col_ms = self._max_autosize_ms / max(1, end - start)

    def _resizeCurrentColumnToContents(self, new_index, old_index):
        """Resize the current column to its contents."""
        if new_index.column() not in self._autosized_cols:
            # Ensure the requested column is fully into view after resizing
            self._resizeVisibleColumnsToContents()
            self._dataTable.scrollTo(new_index)

    def resizeColumnsToContents(
        self,
    ):  # ppw: not sure if this should be public or private?
        """Resize the columns to its contents."""
        self._autosized_cols = set()
        self._resizeColumnsToContents(
            self._table_level, self._table_index, self._max_autosize_ms
        )
        self._update_layout()

    def _change_bgcolor_enable(self, state):
        """
        This is implementet so column min/max is only active when bgcolor is
        """
        self._dataModel._bg_color(state)
        # self.bgcolor_global.setEnabled(not self._is_series and state > 0)

    # def change_format(self):
    #     """
    #     Ask user for display format for floats and use it.
    #     """
    #     format, valid = QInputDialog.getText(
    #         self,
    #         "Format",
    #         "Float formatting",
    #         QLineEdit.Normal,
    #         self._dataModel._getFormat(),
    #     )
    #     if valid:
    #         format = str(format)
    #         try:
    #             format % 1.1
    #         except:  # noqa E722:
    #             msg = "Format ({format}) is incorrect"
    #             QMessageBox.critical(self, "Error", msg)
    #             return
    #         if not format.startswith("%"):
    #             msg = "Format ({format}) should start with '%'"
    #             QMessageBox.critical(self, "Error", msg)
    #             return
    #         self._dataModel._setFormat(format)

    #         format = format[1:]
    #         # self.set_conf('dataframe_format', format)

    def getValue(self):
        """Return modified Dataframe -- this is *not* a copy"""
        # It is import to avoid accessing Qt C++ object as it has probably
        # already been destroyed, due to the Qt.WA_DeleteOnClose attribute
        df = self._dataModel.getData()
        if self._is_series:
            return df.iloc[:, 0]
        else:
            return df

    def _update_header_size(self):
        """Update the column width of the header."""
        self._table_header.resizeColumnsToContents()
        column_count = self._table_header.model().columnCount()
        for index in range(0, column_count):
            if index < column_count:
                column_width = self._dataTable.columnWidth(index)
                header_width = self._table_header.columnWidth(index)
                if column_width > header_width:
                    self._table_header.setColumnWidth(index, column_width)
                else:
                    self._dataTable.setColumnWidth(index, header_width)
            else:
                break

    def _sort_update(self):
        """
        Update the model for all the QTableView objects.
        Uses the model of the dataTable as the base.
        """
        # Update index list calculation
        self._dataModel._recalculateIndex()
        self.setModel(self._dataTable.model())

    def _fetch_more_columns(self):
        """Fetch more data for the header (columns)."""
        self._table_header.model()._fetch_more()

    def _fetch_more_rows(self):
        """Fetch more data for the index (rows)."""
        self._table_index.model()._fetch_more()

    def _resize_to_contents(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self._dataTable.resizeColumnsToContents()
        self._dataModel._fetch_more(columns=True)
        self._dataTable.resizeColumnsToContents()
        self._update_header_size()
        QApplication.restoreOverrideCursor()