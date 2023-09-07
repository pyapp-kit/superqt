from typing import TYPE_CHECKING

from qtpy import API_NAME
from qtpy.QtGui import QImage

if TYPE_CHECKING:
    import numpy as np


def qimage_to_array(img: QImage) -> np.ndarray:
    """Convert QImage to an array.

    Parameters
    ----------
    img : QImage
        QImage to be converted.

    Returns
    -------
    arr : np.ndarray
        Numpy array of type uint8 and shape (h, w, 4). Index [0, 0] is the
        upper-left corner of the rendered region.
    """
    import numpy as np

    # cast to ARGB32 if necessary
    if img.format() != QImage.Format.Format_ARGB32:
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
    b = img.constBits()
    h, w, c = img.height(), img.width(), 4

    # reconcile differences between the `QImage` API for `PySide2` and `PyQt5`
    if API_NAME.startswith("PySide"):
        arr = np.array(b).reshape(h, w, c)
    else:
        b.setsize(h * w * c)
        arr = np.frombuffer(b, np.uint8).reshape(h, w, c)

    # Format of QImage is ARGB32_Premultiplied, but color channels are reversed.
    return arr.take([2, 1, 0, 3], axis=2)
