from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QIcon, QPainter, QPixmap
from qtpy.QtWidgets import QApplication

try:
    from pyconify import svg_path
except ModuleNotFoundError:  # pragma: no cover
    raise ModuleNotFoundError(
        "pyconify is required to use QIconifyIcon. "
        "Please install it with `pip install pyconify` or use the "
        "`pip install superqt[iconify]` extra."
    ) from None

if TYPE_CHECKING:
    from typing import Literal

    Flip = Literal["horizontal", "vertical", "horizontal,vertical"]
    Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]

__all__ = ["QIconifyIcon"]


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

    Parameters are the same as `QIconifyIcon.addKey`, which can be used to add
    additional icons for various modes and states to the same QIcon.

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
        super().__init__()
        if key:
            self.addKey(*key, color=color, flip=flip, rotate=rotate, dir=dir)

    def addKey(
        self,
        *key: str,
        color: str | None = None,
        flip: Flip | None = None,
        rotate: Rotation | None = None,
        dir: str | None = None,
        size: QSize | None = None,
        mode: QIcon.Mode = QIcon.Mode.Normal,
        state: QIcon.State = QIcon.State.Off,
    ) -> QIconifyIcon:
        """Add an icon to this QIcon.

        This is a variant of `QIcon.addFile` that uses an iconify icon keys and
        arguments instead of a file path.

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
            Rotate icon. Must be one of 0, 90, 180, 270, or 0, 1, 2, 3 (equivalent to 0,
            90, 180, 270, respectively)
        dir : str, optional
            If 'dir' is not None, the file will be created in that directory, otherwise
            a default
            [directory](https://docs.python.org/3/library/tempfile.html#tempfile.mkstemp)
            is used.
        size : QSize, optional
            Size specified for the icon, passed to `QIcon.addFile`.
        mode : QIcon.Mode, optional
            Mode specified for the icon, passed to `QIcon.addFile`.
        state : QIcon.State, optional
            State specified for the icon, passed to `QIcon.addFile`.

        Returns
        -------
        QIconifyIcon
            This QIconifyIcon instance, for chaining.
        """
        try:
            path = svg_path(*key, color=color, flip=flip, rotate=rotate, dir=dir)
        except OSError as e:
            warnings.warn(
                f"Error fetching icon: {e}.\nIcon {key} not cached. Using fallback.",
                stacklevel=2,
            )
            self._draw_text_fallback(key)
        else:
            self.addFile(str(path), size or QSize(), mode, state)

        return self

    def _draw_text_fallback(self, key: tuple[str, ...]) -> None:
        if style := QApplication.style():
            pixmap = style.standardPixmap(style.StandardPixmap.SP_MessageBoxQuestion)
        else:
            pixmap = QPixmap(18, 18)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "?")
            painter.end()

        self.addPixmap(pixmap)
