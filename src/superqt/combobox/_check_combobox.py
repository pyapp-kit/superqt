from enum import Enum, auto
from typing import Any, List, Union, cast

from qtpy.QtCore import QEvent, QModelIndex, Qt
from qtpy.QtGui import QStandardItem, QStandardItemModel
from qtpy.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox, QStylePainter


class QCheckComboBox(QComboBox):
    """
    A combobox with a check for each item inserted.
    based on https://stackoverflow.com/questions/47575880/qcombobox-set-title-text-regardless-of-items
    """

    class QCheckComboBoxLabelType(Enum):
        """Label type"""

        STRING = auto()
        SELECTED_ITEMS = auto()

    _label_text: str = "Select items"
    _label_type: QCheckComboBoxLabelType = QCheckComboBoxLabelType.STRING

    def __init__(self) -> None:
        """Initializes the widget"""
        super().__init__()
        self.view().pressed.connect(self._handleItemPressed)  # type: ignore
        self.view().doubleClicked.connect(self._handleItemPressed)  # type: ignore
        self._changed = False

    def model(self) -> QStandardItemModel:
        # this is true, but annotated incorrectly in pyside2
        return cast(QStandardItemModel, super().model())

    def _update_label_text_with_selected_items(self) -> None:
        checked_indices = self.checkedIndices()
        selected_text_list = []
        for index in checked_indices:
            selected_text_list.append(self.itemText(index))
        self.setLabelText(", ".join(selected_text_list))

    def setLabelText(self, label_text: str) -> None:
        """Sets the label text"""
        self._label_text = label_text
        self.repaint()

    def labelText(self) -> str:
        return self._label_text

    def setLabelType(self, label_type: QCheckComboBoxLabelType) -> None:
        """Sets the label type"""
        self._label_type = label_type
        if label_type == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS:
            self._update_label_text_with_selected_items()

    def labelType(self) -> QCheckComboBoxLabelType:
        """Returns label type"""
        return self._label_type

    def _handleItemPressed(self, index: QModelIndex) -> None:
        """Updates item checked status"""
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

        if self._label_type == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS:
            self._update_label_text_with_selected_items()
        self._changed = True

    def addItem(self, text: str, userData: Any = None, checked: bool = True) -> None:
        """Overrides the combobox additem to make sure it is chackable"""
        super().addItem(text, userData)
        item: QStandardItem = self.model().item(self.count() - 1, self.modelColumn())
        item.setCheckable(True)
        self.setItemChecked(self.count() - 1, checked=checked)
        if (
            self._label_type == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS
            and checked
        ):
            self._update_label_text_with_selected_items()

    def addItems(
        self, texts: List[str], checked: Union[bool, List[bool]] = True
    ) -> None:
        """Overirdes the combobox addItems to make sure it is checkable"""
        if isinstance(checked, bool):
            checked = [checked] * len(texts)

        for text, checked_value in zip(texts, checked):
            self.addItem(text=text, userData=None, checked=checked_value)

        if (
            self._label_type == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS
            and any(checked)
        ):
            self._update_label_text_with_selected_items()

    def hidePopup(self) -> None:
        """Override hidePopup to disable it if an item state has changed"""
        if not self._changed:
            super().hidePopup()
        self._changed = False

    def itemChecked(self, index: int) -> bool:
        """Returns current checked state as boolean"""
        item: QStandardItem = self.model().item(index, self.modelColumn())
        return bool(item.checkState() == Qt.CheckState.Checked)

    def setItemChecked(self, index: int, checked: bool = True) -> None:
        """Sets the status"""
        item: QStandardItem = self.model().item(index)
        checked_state_old = item.checkState()
        checked_state_new = (
            Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        )

        # Stopping condition
        if checked_state_old == checked_state_new:
            return

        item.setCheckState(checked_state_new)

        if self._label_type == QCheckComboBox.QCheckComboBoxLabelType.SELECTED_ITEMS:
            self._update_label_text_with_selected_items()

    def setAllItemChecked(self, checked: bool = True) -> None:
        """Set all item checked status in one go"""
        for i in range(self.count()):
            self.setItemChecked(i, checked=checked)

    def checkedIndices(self) -> List[int]:
        """Returns the checked indices"""
        indecies = []
        for i in range(self.count()):
            item = self.model().item(i)
            if item.checkState() == Qt.CheckState.Checked:
                indecies.append(i)
        return indecies

    def uncheckedIndices(self) -> List[int]:
        """Returns teh unchecked indices"""
        indecies = []
        for i in range(self.count()):
            item = self.model().item(i)
            if item.checkState() == Qt.CheckState.Unchecked:
                indecies.append(i)
        return indecies

    def paintEvent(self, event: QEvent) -> None:
        """Overrides the paint event to update the label"""
        painter = QStylePainter(self)
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        opt.currentText = self._label_text
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, opt)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, opt)
