from typing import Generic, Iterable, Sequence, TypeVar, overload

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QSlider, QWidget

T = TypeVar("T")


class QCategoricalSlider(QSlider, Generic[T]):
    """A Slider that can only take on a finite number of values."""

    categoryChanged = Signal(object)
    categoriesChanged = Signal(tuple)

    @overload
    def __init__(
        self,
        parent: QWidget | None = ...,
        /,
        *,
        categories: Iterable[T] = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        orientation: Qt.Orientation,
        parent: QWidget | None = ...,
        /,
        *,
        categories: Iterable[T] = ...,
    ) -> None: ...

    def __init__(
        self, *args: Qt.Orientation | QWidget | None, categories: Iterable[T] = ()
    ) -> None:
        # default to horizontal orientation
        if len(args) == 0:
            args = (Qt.Orientation.Horizontal, None)
        elif len(args) == 1:
            args = (Qt.Orientation.Horizontal, args[0])
        super().__init__(*args)  # type: ignore [arg-type]

        self._categories: Sequence[T] = ()
        self.setCategories(categories)
        self.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.setTickInterval(1)
        self.valueChanged.connect(self._on_value_changed)

    def categories(self) -> Sequence[T]:
        """Return the categories of the slider."""
        return self._categories

    def setCategories(self, categories: Iterable[T]) -> None:
        """Set the categories of the slider."""
        self._categories = tuple(categories)
        self.setRange(0, len(self._categories) - 1)
        self.categoriesChanged.emit(self._categories)

    def category(self) -> T:
        """Return the current categorical value of the slider."""
        try:
            return self._categories[super().value()]
        except IndexError:
            return None

    def setCategory(self, value: T) -> None:
        """Set the current categorical value of the slider."""
        try:
            # we could consider indexing this up-front during setCategories
            # to save .index() calls here
            idx = self._categories.index(value)
        except ValueError:
            # the behavior of the original QSlider is to (quietly) pin to the nearest
            # value when the value is out of range.  Here we do nothing.
            return None
        super().setValue(idx)

    def _on_value_changed(self, value: int) -> None:
        self.categoryChanged.emit(self._categories[value])
