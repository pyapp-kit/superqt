import sys
from typing import TYPE_CHECKING

from qtpy.QtGui import QImage

if TYPE_CHECKING:
    import numpy as np


def qimage_to_array(img: QImage) -> "np.ndarray":
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

    h, w, c = img.height(), img.width(), 4

    # pyside returns a memoryview, pyqt returns a sizeless void pointer
    b = img.constBits()  # Returns a pointer to the first pixel data.
    if hasattr(b, "setsize"):
        b.setsize(h * w * c)

    # reshape to h, w, c
    arr = np.frombuffer(b, np.uint8).reshape(h, w, c)

    # reverse channel colors for numpy
    # On big endian we need to specify a different order
    if sys.byteorder == "big":
        return arr.take([1, 2, 3, 0], axis=2)  # pragma: no cover
    else:
        return arr.take([2, 1, 0, 3], axis=2)
