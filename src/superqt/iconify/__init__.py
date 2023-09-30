from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtGui import QIcon

if TYPE_CHECKING:
    from typing import Literal

    Flip = Literal["horizontal", "vertical", "horizontal,vertical"]
    Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]


class QIconifyIcon(QIcon):
    """QIcon backed by an iconify icon.

    This class is a thin wrapper around the
    [pyconify](https://github.com/pyapp-kit/pyconify) `temp_svg` function. It creates a
    temporary SVG file and uses it as the source for a QIcon. SVGs are cached to disk,
    and persist across sessions (until `pyconify.clear_cache()` is called).

    Iconify includes 150,000+ icons from most major icon sets including Bootstrap,
    FontAwesome, Material Design, and many more.

    Search availble icons at https://icon-sets.iconify.design

    Once you find one you like, use the key in the format `"prefix:name"` to create an
    icon:  `QIconifyIcon("bi:bell")`.

    Parameters
    ----------
    *key: str
        Icon set prefix and name. May be passed as a single string in the format
        `"prefix:name"` or as two separate strings: `'prefix', 'name'`.
    color : str, optional
        Icon color. Replaces currentColor with specific color, resulting in icon with
        hardcoded palette.
    flip : str, optional
        Flip icon.
    rotate : str | int, optional
        Rotate icon. If an integer is provided, it is assumed to be in degrees.
    prefix : str, optional
        If not None, the temp file name will begin with that prefix, otherwise a default
        prefix is used.
    dir : str, optional
        If 'dir' is not None, the file will be created in that directory, otherwise a
        default directory is used.

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
        prefix: str | None = None,
        dir: str | None = None,
    ):
        try:
            from pyconify import temp_svg
        except ImportError:
            raise ImportError(
                "pyconify is required to use QIconifyIcon. "
                "Please install it with `pip install pyconify`"
            ) from None
        self.path = temp_svg(
            *key, color=color, flip=flip, rotate=rotate, prefix=prefix, dir=dir
        )
        super().__init__(self.path)
