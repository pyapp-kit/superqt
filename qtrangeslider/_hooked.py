from .qtcompat.QtWidgets import QSlider


class _HookedSlider(QSlider):
    def _post_get_hook(self, value):
        return value

    def _pre_set_hook(self, value):
        return value

    def value(self) -> float:  # type: ignore[override]
        return float(self._post_get_hook(super().value()))

    def setValue(self, value: float) -> None:
        super().setValue(self._pre_set_hook(value))

    def minimum(self) -> float:  # type: ignore[override]
        return self._post_get_hook(super().minimum())

    def setMinimum(self, minimum: float):
        super().setMinimum(self._pre_set_hook(minimum))

    def maximum(self) -> float:  # type: ignore[override]
        return self._post_get_hook(super().maximum())

    def setMaximum(self, maximum: float):
        super().setMaximum(self._pre_set_hook(maximum))

    def singleStep(self) -> float:  # type: ignore[override]
        return self._post_get_hook(super().singleStep())

    def setSingleStep(self, step: float):
        super().setSingleStep(self._pre_set_hook(step))

    def pageStep(self) -> float:  # type: ignore[override]
        return self._post_get_hook(super().pageStep())

    def setPageStep(self, step: float) -> None:
        super().setPageStep(self._pre_set_hook(step))

    def setRange(self, min: float, max: float) -> None:
        super().setRange(self._pre_set_hook(min), self._pre_set_hook(max))

    # def sliderChange(self, change) -> None:
    #     if change == QSlider.SliderValueChange:
    #         self.valueChanged.emit(self.value())
    #     if change == QSlider.SliderRangeChange:
    #         self.rangeChanged.emit(self.minimum(), self.maximum())
    #     return super().sliderChange(change)
