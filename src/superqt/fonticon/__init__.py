from __future__ import annotations

__all__ = [
    "ENTRY_POINT",
    "Animation",
    "IconFont",
    "IconFontMeta",
    "IconOpts",
    "QIconifyIcon",
    "addFont",
    "font",
    "icon",
    "pulse",
    "setTextIcon",
    "spin",
]

from typing import TYPE_CHECKING

from ._animations import Animation, pulse, spin
from ._iconfont import IconFont, IconFontMeta
from ._plugins import FontIconManager as _FIM
from ._qfont_icon import DEFAULT_SCALING_FACTOR, IconOptionDict, IconOpts
from ._qfont_icon import QFontIconStore as _QFIS

if TYPE_CHECKING:
    from qtpy.QtGui import QFont, QTransform
    from qtpy.QtWidgets import QWidget

    from ._qfont_icon import QFontIcon, ValidColor

ENTRY_POINT = _FIM.ENTRY_POINT


# FIXME: currently, an Animation requires a *pre-bound* QObject.  which makes it very
# awkward to use animations when declaratively listing icons.  It would be much better
# to have a way to find the widget later, to execute the animation... short of that, I
# think we should take animation off of `icon` here, and suggest that it be an
# an additional convenience method after the icon has been bound to a QObject.
def icon(
    glyph_key: str,
    scale_factor: float = DEFAULT_SCALING_FACTOR,
    color: ValidColor | None = None,
    opacity: float = 1,
    animation: Animation | None = None,
    transform: QTransform | None = None,
    states: dict[str, IconOptionDict | IconOpts] | None = None,
) -> QFontIcon:
    """Create a QIcon for `glyph_key`, with a number of optional settings.

    The `glyph_key` (e.g. 'fa5s.smile') represents a Font-family & style, and a glyph.
    In most cases, the key should be provided by a plugin in the environment, like:

    - [fonticon-fontawesome5](https://pypi.org/project/fonticon-fontawesome5/) ('fa5s' &
      'fa5r' prefixes)
    - [fonticon-materialdesignicons6](https://pypi.org/project/fonticon-materialdesignicons6/)
      ('mdi6' prefix)

    ...but fonts can also be added manually using [`addFont`][superqt.fonticon.addFont].

    Parameters
    ----------
    glyph_key : str
        String encapsulating a font-family, style, and glyph. e.g. 'fa5s.smile'.
    scale_factor : float, optional
        Scale factor (fraction of widget height), When widget icon is painted on widget,
        it will use `font.setPixelSize(round(wdg.height() * scale_factor))`.
        by default 0.875.
    color : ValidColor, optional
        Color for the font, by default None. (e.g. The default `QColor`)
        Valid color types include `QColor`, `int`, `str`, `Qt.GlobalColor`, `tuple` (of
        integer: RGB[A]) (anything that can be passed to `QColor`).
    opacity : float, optional
        Opacity of icon, by default 1
    animation : Animation, optional
        Animation for the icon.  A subclass of superqt.fonticon.Animation, that provides
        a concrete `animate` method. (see "spin" and "pulse" for examples).
        by default None.
    transform : QTransform, optional
        A `QTransform` to apply when painting the icon, by default None
    states : dict, optional
        Provide additional styling for the icon in different states.  `states` must be
        a mapping of string to dict, where:

        - the key represents a `QIcon.State` ("on", "off"), a `QIcon.Mode` ("normal",
          "active", "selected", "disabled"), or any combination of a state & mode
          separated by an underscore (e.g. "off_active", "selected_on", etc...).
        - the value is a dict with all of the same key/value meanings listed above as
          parameters to this function (e.g. `glyph_key`, `color`,`scale_factor`,
          `animation`, etc...)

        Missing keys in the state dicts will be taken from the default options, provided
        by the parameters above.

    Returns
    -------
    QFontIcon
        A subclass of QIcon.  Can be used wherever QIcons are used, such as
        `widget.setIcon()`

    Examples
    --------
    simple example (using the string `'fa5s.smile'` assumes the `fonticon-fontawesome5`
    plugin is installed)

    >>> btn = QPushButton()
    >>> btn.setIcon(icon("fa5s.smile"))

    can also directly import from fonticon_fa5
    >>> from fonticon_fa5 import FA5S
    >>> btn.setIcon(icon(FA5S.smile))

    with animation
    >>> btn2 = QPushButton()
    >>> btn2.setIcon(icon(FA5S.spinner, animation=pulse(btn2)))

    complicated example
    >>> btn = QPushButton()
    >>> btn.setIcon(
    ...     icon(
    ...         FA5S.ambulance,
    ...         color="blue",
    ...         states={
    ...             "active": {
    ...                 "glyph": FA5S.bath,
    ...                 "color": "red",
    ...                 "scale_factor": 0.5,
    ...                 "animation": pulse(btn),
    ...             },
    ...             "disabled": {
    ...                 "color": "green",
    ...                 "scale_factor": 0.8,
    ...                 "animation": spin(btn),
    ...             },
    ...         },
    ...     )
    ... )
    >>> btn.setIconSize(QSize(256, 256))
    >>> btn.show()

    """
    return _QFIS.instance().icon(
        glyph_key,
        scale_factor=scale_factor,
        color=color,
        opacity=opacity,
        animation=animation,
        transform=transform,
        states=states or {},
    )


def setTextIcon(widget: QWidget, glyph_key: str, size: float | None = None) -> None:
    """Set text on a widget to a specific font & glyph.

    This is an alternative to setting a QIcon with a pixmap.  It may be easier to
    combine with dynamic stylesheets.

    Parameters
    ----------
    widget : QWidget
        A widget supporting a `setText` method.
    glyph_key : str
        String encapsulating a font-family, style, and glyph. e.g. 'fa5s.smile'.
    size : int, optional
        Size for QFont.  passed to `setPixelSize`, by default None
    """
    return _QFIS.instance().setTextIcon(widget, glyph_key, size)


def font(font_prefix: str, size: int | None = None) -> QFont:
    """Create QFont for `font_prefix`.

    Parameters
    ----------
    font_prefix : str
        Font_prefix, such as 'fa5s' or 'mdi6', representing a font-family and style.
    size : int, optional
        Size for QFont.  passed to `setPixelSize`, by default None

    Returns
    -------
    QFont
        QFont instance that can be used to add fonticons to widgets.
    """
    return _QFIS.instance().font(font_prefix, size)


def addFont(
    filepath: str, prefix: str, charmap: dict[str, str] | None = None
) -> tuple[str, str] | None:
    """Add OTF/TTF file at `filepath` to the registry under `prefix`.

    If you'd like to later use a fontkey in the form of `prefix.some-name`, then
    `charmap` must be provided and provide a mapping for all of the glyph names
    to their unicode numbers. If a charmap is not provided, glyphs must be directly
    accessed with their unicode as something like `key.\uffff`.

    !!! Note
        in most cases, users will not need this. Instead, they should install a
        font plugin, like:

        - [fonticon-fontawesome5](https://pypi.org/project/fonticon-fontawesome5/)
        - [fonticon-materialdesignicons6](https://pypi.org/project/fonticon-materialdesignicons6/)

    Parameters
    ----------
    filepath : str
        Path to an OTF or TTF file containing the fonts
    prefix : str
        A prefix that will represent this font file when used for lookup.  For example,
        'fa5s' for 'Font-Awesome 5 Solid'.
    charmap : Dict[str, str], optional
        optional mapping for all of the glyph names to their unicode numbers.
        See note above.

    Returns
    -------
    Tuple[str, str], optional
        font-family and font-style for the file just registered, or `None` if
        something goes wrong.
    """
    return _QFIS.instance().addFont(filepath, prefix, charmap)


del DEFAULT_SCALING_FACTOR
