from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QIcon

if TYPE_CHECKING:
    from typing import Literal

    Flip = Literal["horizontal", "vertical", "horizontal,vertical"]
    Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]


class QIconifyIcon(QIcon):
    """QIcon backed by an iconify icon.

    Iconify includes 150,000+ icons from most major icon sets including Bootstrap,
    FontAwesome, Material Design, and many more.

    Search availble icons at https://icon-sets.iconify.design
    Once you find one you like, use the key in the format `"prefix:name"` to create an
    icon:  `QIconifyIcon("bi:bell")`.

    This class is a thin wrapper around the
    [pyconify](https://github.com/pyapp-kit/pyconify) `svg_path` function. It pulls SVGs
    from iconify, creates a temporary SVG file and uses it as the source for a QIcon.
    SVGs are cached to disk, and persist across sessions (until `pyconify.clear_cache()`
    is called).

    Parameters
    ----------
    *key: str
        Icon set prefix and name. May be passed as a single string in the format
        `"prefix:name"` or as two separate strings: `'prefix', 'name'`.
    color : str, optional
        Icon color. If not provided, the icon will appear black (the icon fill color
        will be set to the string "currentColor").
    flip : str, optional
        Flip icon.  Must be one of "horizontal", "vertical", "horizontal,vertical"
    rotate : str | int, optional
        Rotate icon. Must be one of 0, 90, 180, 270,
        or 0, 1, 2, 3 (equivalent to 0, 90, 180, 270, respectively)
    dir : str, optional
        If 'dir' is not None, the file will be created in that directory, otherwise a
        default
        [directory](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp) is
        used.

    Examples
    --------
    >>> from qtpy.QtWidgets import QPushButton
    >>> from superqt import QIconifyIcon
    >>> btn = QPushButton()
    >>> icon = QIconifyIcon("bi:alarm-fill", color="red", rotate=90)
    >>> btn.setIcon(icon)
    """

    def __init__(
        self,
        *key: str,
        color: str | None = None,
        flip: Flip | None = None,
        rotate: Rotation | None = None,
        dir: str | None = None,
    ):
        try:
            from pyconify import svg_path
        except ModuleNotFoundError as e:  # pragma: no cover
            raise ImportError(
                "pyconify is required to use QIconifyIcon. "
                "Please install it with `pip install pyconify` or use the "
                "`pip install superqt[iconify]` extra."
            ) from e
        self.path = svg_path(*key, color=color, flip=flip, rotate=rotate, dir=dir)
        super().__init__(str(self.path))
