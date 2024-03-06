from typing import Any

from superqt.cmap import QColormapComboBox

from ._color_combobox import QColorComboBox
from ._enum_combobox import QEnumComboBox
from ._searchable_combo_box import QSearchableComboBox

__all__ = (
    "QColorComboBox",
    "QColormapComboBox",
    "QEnumComboBox",
    "QSearchableComboBox",
)


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "QColormapComboBox":
        from superqt.cmap import QColormapComboBox

        return QColormapComboBox
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
