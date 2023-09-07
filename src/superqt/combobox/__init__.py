from typing import TYPE_CHECKING, Any

from ._enum_combobox import QEnumComboBox
from ._searchable_combo_box import QSearchableComboBox

if TYPE_CHECKING:
    from superqt.cmap import QColormapComboBox


__all__ = ("QEnumComboBox", "QSearchableComboBox", "QColormapComboBox")


def __getattr__(name: str) -> Any:
    if name == "QColormapComboBox":
        from superqt.cmap import QColormapComboBox

        return QColormapComboBox
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
