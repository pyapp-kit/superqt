from __future__ import annotations

from qtpy.QtCore import QPoint, QRect, QSize, Qt
from qtpy.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QStyle, QWidget


class QFlowLayout(QLayout):
    """Layout that handles different window sizes.

    The widget placement changes depending on the width of the application window.

    Code translated from C++ at:
    <https://code.qt.io/cgit/qt/qtbase.git/tree/examples/widgets/layouts/flowlayout>

    described at: <https://doc.qt.io/qt-6/qtwidgets-layouts-flowlayout-example.html>

    See also: <https://doc.qt.io/qt-6/layout.html>

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget, by default None
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._item_list: list[QLayoutItem] = []
        self._h_space = -1
        self._v_space = -1

    def __del__(self) -> None:
        while item := self.takeAt(0):
            del item

    def addItem(self, item: QLayoutItem | None) -> None:
        """Add an item to the layout."""
        if item:
            self._item_list.append(item)

    def setHorizontalSpacing(self, space: int | None) -> None:
        """Set the horizontal spacing.

        If None or -1, the spacing is set to the default value based on the style
        of the parent widget.
        """
        self._h_space = -1 if space is None else space

    def horizontalSpacing(self) -> int:
        """Return the horizontal spacing."""
        if self._h_space >= 0:
            return self._h_space
        return self._smartSpacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def setVerticalSpacing(self, space: int | None) -> None:
        """Set the vertical spacing.

        If None or -1, the spacing is set to the default value based on the style
        of the parent widget.
        """
        self._v_space = -1 if space is None else space

    def verticalSpacing(self) -> int:
        """Return the vertical spacing."""
        if self._v_space >= 0:
            return self._v_space
        return self._smartSpacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def expandingDirections(self) -> Qt.Orientation:
        """Return the expanding directions.

        These are the Qt::Orientations in which the layout can make use of more space
        than its sizeHint().
        """
        return Qt.Orientation.Horizontal

    def hasHeightForWidth(self) -> bool:
        """Return whether the layout handles height for width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Return the height for a given width.

        `heightForWidth()` passes the width on to _doLayout() which in turn uses the
        width as an argument for the layout rect, i.e., the bounds in which the items
        are laid out. This rect does not include the layout margin().
        """
        return self._doLayout(QRect(0, 0, width, 0), True)

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return the item at the given index, or None if the index is out of range."""
        try:
            return self._item_list[index]
        except IndexError:
            return None

    def minimumSize(self) -> QSize:
        """Return the minimum size of the layout."""
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(), margins.top() + margins.bottom()
        )
        return size

    def setGeometry(self, rect: QRect) -> None:
        """Set the geometry of the layout.

        This triggers a re-layout of the items.
        """
        super().setGeometry(rect)
        self._doLayout(rect)

    def sizeHint(self) -> QSize:
        """Return the size hint of the layout."""
        return self.minimumSize()

    def takeAt(self, index: int) -> QLayoutItem | None:
        """Remove and return the item at the given index.  Or return None."""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def _doLayout(self, rect: QRect, test_only: bool = False) -> int:
        """Arrange the items in the layout.

        If test_only is True, the items are not actually laid out, but the height
        that the layout would have with the given width is returned.
        """
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)  # type: ignore
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            if (wid := item.widget()) and (style := wid.style()):
                space_x = self.horizontalSpacing()
                space_y = self.verticalSpacing()
                if space_x == -1:
                    space_x = style.layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Horizontal,
                    )
                if space_y == -1:
                    space_y = style.layoutSpacing(
                        QSizePolicy.ControlType.PushButton,
                        QSizePolicy.ControlType.PushButton,
                        Qt.Orientation.Vertical,
                    )

                # next_x is the x-coordinate of the right edge of the item
                next_x = x + item.sizeHint().width() + space_x
                # if the item is not the first one in a line, add the spacing
                # to the left of it
                if next_x - space_x > effective_rect.right() and line_height > 0:
                    x = effective_rect.x()
                    y = y + line_height + space_y
                    next_x = x + item.sizeHint().width() + space_x
                    line_height = 0

                # if this is not a test run, move the item to its proper place
                if not test_only:
                    item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

                x = next_x
                line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom

    def _smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        """Return the smart spacing based on the style of the parent widget."""
        if isinstance(parent := self.parent(), QWidget) and (style := parent.style()):
            return style.pixelMetric(pm, None, parent)
        return -1
