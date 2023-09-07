try:
    import cmap
except ImportError as e:
    raise ImportError(
        "The cmap package is required to use superqt colormap utilities. "
        "Install it with `pip install cmap` or `pip install superqt[cmap]`."
    ) from e
else:
    del cmap

from ._catalog_combo import CmapCatalogComboBox
from ._cmap_combo import QColormapComboBox
from ._cmap_item_delegate import ColormapItemDelegate
from ._cmap_line_edit import ColormapLineEdit
from ._cmap_utils import draw_colormap

__all__ = [
    "ColormapItemDelegate",
    "draw_colormap",
    "ColormapLineEdit",
    "CmapCatalogComboBox",
    "QColormapComboBox",
]
