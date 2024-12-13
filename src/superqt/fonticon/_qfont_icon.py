from __future__ import annotations

import warnings
from collections import abc, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Union, cast

from qtpy import QT_VERSION
from qtpy.QtCore import QObject, QPoint, QRect, QSize, Qt
from qtpy.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QIcon,
    QIconEngine,
    QPainter,
    QPixmap,
    QPixmapCache,
    QTransform,
)
from qtpy.QtWidgets import QApplication, QStyleOption, QWidget
from typing_extensions import TypedDict

from superqt.utils import QMessageHandler

if TYPE_CHECKING:
    from ._animations import Animation


class Unset:
    def __repr__(self) -> str:
        return "UNSET"


_Unset = Unset()

# A 16 pixel-high icon yields a font size of 14, which is pixel perfect
# for font-awesome. 16 * 0.875 = 14
# The reason why the glyph size is smaller than the icon size is to
# account for font bearing.
DEFAULT_SCALING_FACTOR = 0.875
DEFAULT_OPACITY = 1
ValidColor = Union[
    QColor,
    int,
    str,
    Qt.GlobalColor,
    tuple[int, int, int, int],
    tuple[int, int, int],
    None,
]

StateOrMode = Union[QIcon.State, QIcon.Mode]
StateModeKey = Union[StateOrMode, str, Sequence[StateOrMode]]
_SM_MAP: dict[str, StateOrMode] = {
    "on": QIcon.State.On,
    "off": QIcon.State.Off,
    "normal": QIcon.Mode.Normal,
    "active": QIcon.Mode.Active,
    "selected": QIcon.Mode.Selected,
    "disabled": QIcon.Mode.Disabled,
}


def _norm_state_mode(key: StateModeKey) -> tuple[QIcon.State, QIcon.Mode]:
    """Return state/mode tuple given a variety of valid inputs.

    Input can be either a string, or a sequence of state or mode enums.
    Strings can be any combination of on, off, normal, active, selected, disabled,
    sep by underscore.
    """
    _sm: Sequence[StateOrMode]
    if isinstance(key, str):
        try:
            _sm = [_SM_MAP[k.lower()] for k in key.split("_")]
        except KeyError as e:
            raise ValueError(
                f"{key!r} is not a valid state key, must be a combination of {{on, "
                "off, active, disabled, selected, normal} separated by underscore"
            ) from e
    else:
        _sm = key if isinstance(key, abc.Sequence) else [key]

    state = next((i for i in _sm if isinstance(i, QIcon.State)), QIcon.State.Off)
    mode = next((i for i in _sm if isinstance(i, QIcon.Mode)), QIcon.Mode.Normal)
    return state, mode


class IconOptionDict(TypedDict, total=False):
    glyph_key: str
    scale_factor: float
    color: ValidColor
    opacity: float
    animation: Animation | None
    transform: QTransform | None


# public facing, for a nicer IDE experience than a dict
# The difference between IconOpts and _IconOptions is that all of IconOpts
# all default to `_Unset` and are intended to extend some base/default option
# IconOpts are *not* guaranteed to be fully capable of rendering an icon, whereas
# IconOptions are.
@dataclass
class IconOpts:
    """Options for rendering an icon.

    Parameters
    ----------
    glyph_key : str, optional
        The key of the glyph to use, e.g. `'fa5s.smile'`, by default `None`
    scale_factor : float, optional
        The scale factor to use, by default `None`
    color : ValidColor, optional
        The color to use, by default `None`. Colors may be specified as a string,
        `QColor`, `Qt.GlobalColor`, or a 3 or 4-tuple of integers.
    opacity : float, optional
        The opacity to use, by default `None`
    animation : Animation, optional
        The animation to use, by default `None`
    """

    glyph_key: str | Unset = _Unset
    scale_factor: float | Unset = _Unset
    color: ValidColor | Unset = _Unset
    opacity: float | Unset = _Unset
    animation: Animation | Unset | None = _Unset
    transform: QTransform | Unset | None = _Unset

    def dict(self) -> IconOptionDict:
        # not using asdict due to pickle errors on animation
        d = {k: v for k, v in vars(self).items() if v is not _Unset}
        return cast(IconOptionDict, d)


@dataclass
class _IconOptions:
    """The set of options needed to render a font in a single State/Mode."""

    glyph_key: str
    scale_factor: float = DEFAULT_SCALING_FACTOR
    color: ValidColor = None
    opacity: float = DEFAULT_OPACITY
    animation: Animation | None = None
    transform: QTransform | None = None

    def _update(self, icon_opts: IconOpts) -> _IconOptions:
        return _IconOptions(**{**vars(self), **icon_opts.dict()})

    def dict(self) -> IconOptionDict:
        # not using asdict due to pickle errors on animation
        return cast(IconOptionDict, vars(self))


class _QFontIconEngine(QIconEngine):
    _opt_hash: str = ""

    def __init__(self, options: _IconOptions):
        super().__init__()
        self._opts: defaultdict[QIcon.State, dict[QIcon.Mode, _IconOptions | None]] = (
            defaultdict(dict)
        )
        self._opts[QIcon.State.Off][QIcon.Mode.Normal] = options
        self.update_hash()

    @property
    def _default_opts(self) -> _IconOptions:
        return cast(_IconOptions, self._opts[QIcon.State.Off][QIcon.Mode.Normal])

    def _add_opts(self, state: QIcon.State, mode: QIcon.Mode, opts: IconOpts) -> None:
        self._opts[state][mode] = self._default_opts._update(opts)
        self.update_hash()

    def clone(self) -> QIconEngine:  # pragma: no cover
        ico = _QFontIconEngine(self._default_opts)
        ico._opts = self._opts.copy()
        return ico

    def _get_opts(self, state: QIcon.State, mode: QIcon.Mode) -> _IconOptions:
        opts = self._opts[state].get(mode)
        if opts:
            return opts

        opp_state = QIcon.State.Off if state == QIcon.State.On else QIcon.State.On
        if mode in (QIcon.Mode.Disabled, QIcon.Mode.Selected):
            opp_mode = (
                QIcon.Mode.Disabled
                if mode == QIcon.Mode.Selected
                else QIcon.Mode.Selected
            )
            for m, s in [
                (QIcon.Mode.Normal, state),
                (QIcon.Mode.Active, state),
                (mode, opp_state),
                (QIcon.Mode.Normal, opp_state),
                (QIcon.Mode.Active, opp_state),
                (opp_mode, state),
                (opp_mode, opp_state),
            ]:
                opts = self._opts[s].get(m)
                if opts:
                    return opts
        else:
            opp_mode = (
                QIcon.Mode.Active if mode == QIcon.Mode.Normal else QIcon.Mode.Normal
            )
            for m, s in [
                (opp_mode, state),
                (mode, opp_state),
                (opp_mode, opp_state),
                (QIcon.Mode.Disabled, state),
                (QIcon.Mode.Selected, state),
                (QIcon.Mode.Disabled, opp_state),
                (QIcon.Mode.Selected, opp_state),
            ]:
                opts = self._opts[s].get(m)
                if opts:
                    return opts
        return self._default_opts

    def paint(
        self,
        painter: QPainter,
        rect: QRect,
        mode: QIcon.Mode,
        state: QIcon.State,
    ) -> None:
        opts = self._get_opts(state, mode)

        char, family, style = QFontIconStore.key2glyph(opts.glyph_key)

        # font
        font = QFont()
        font.setFamily(family)  # set separately for Qt6
        font.setPixelSize(round(rect.height() * opts.scale_factor))
        if style:
            font.setStyleName(style)

        # color
        if isinstance(opts.color, tuple):
            color_args = opts.color
        else:
            color_args = (opts.color,) if opts.color else ()

        # animation
        if opts.animation is not None:
            opts.animation.animate(painter)

        # animation
        if opts.transform is not None:
            painter.setTransform(opts.transform, True)

        painter.save()
        painter.setPen(QColor(*color_args))
        painter.setOpacity(opts.opacity)
        painter.setFont(font)
        with QMessageHandler():  # avoid "Populating font family aliases" warning
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        # first look in cache
        pmckey = self._pmcKey(size, mode, state)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "QPixmapCache.find")
            pm = QPixmapCache.find(pmckey) if pmckey else None
        if pm:
            return pm
        pixmap = QPixmap(size)
        if not size.isValid():
            return pixmap
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        painter.end()

        # Apply palette-based styles for disabled/selected modes
        # unless the user has specifically set a color for this mode/state
        if mode != QIcon.Mode.Normal:
            ico_opts = self._opts[state].get(mode)
            if not ico_opts or not ico_opts.color:
                opt = QStyleOption()
                opt.palette = QGuiApplication.palette()
                generated = QApplication.style().generatedIconPixmap(mode, pixmap, opt)
                if not generated.isNull():
                    pixmap = generated

        if pmckey and not pixmap.isNull():
            QPixmapCache.insert(pmckey, pixmap)

        return pixmap

    def _pmcKey(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> str:
        # Qt6-style enums
        if self._get_opts(state, mode).animation:
            return ""
        if hasattr(mode, "value"):
            mode = mode.value
        if hasattr(state, "value"):
            state = state.value
        k = ((((((size.width()) << 11) | size.height()) << 11) | mode) << 4) | state
        return f"$superqt_{self._opt_hash}_{hex(k)}"

    def update_hash(self) -> None:
        hsh = id(self)
        for state, d in self._opts.items():
            for mode, opts in d.items():
                if not opts:
                    continue
                hsh += hash(
                    hash(opts.glyph_key) + hash(opts.color) + hash(state) + hash(mode)
                )
        self._opt_hash = hex(hsh)


class QFontIcon(QIcon):
    def __init__(self, options: _IconOptions) -> None:
        self._engine = _QFontIconEngine(options)
        super().__init__(self._engine)

    def addState(
        self,
        state: QIcon.State = QIcon.State.Off,
        mode: QIcon.Mode = QIcon.Mode.Normal,
        glyph_key: str | Unset = _Unset,
        scale_factor: float | Unset = _Unset,
        color: ValidColor | Unset = _Unset,
        opacity: float | Unset = _Unset,
        animation: Animation | Unset | None = _Unset,
        transform: QTransform | Unset | None = _Unset,
    ) -> None:
        """Set icon options for a specific mode/state."""
        if glyph_key is not _Unset:
            QFontIconStore.key2glyph(glyph_key)  # type: ignore

        _opts = IconOpts(
            glyph_key=glyph_key,
            scale_factor=scale_factor,
            color=color,
            opacity=opacity,
            animation=animation,
            transform=transform,
        )
        self._engine._add_opts(state, mode, _opts)


class QFontIconStore(QObject):
    # map of key -> (font_family, font_style)
    _LOADED_KEYS: ClassVar[dict[str, tuple[str, str]]] = {}

    # map of (font_family, font_style) -> character (char may include key)
    _CHARMAPS: ClassVar[dict[tuple[str, str | None], dict[str, str]]] = {}

    # singleton instance, use `instance()` to retrieve
    __instance: ClassVar[QFontIconStore | None] = None

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        if tuple(cast(str, QT_VERSION).split(".")) < ("6", "0"):
            # QT6 drops this
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    @classmethod
    def instance(cls) -> QFontIconStore:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def clear(cls) -> None:
        cls._LOADED_KEYS.clear()
        cls._CHARMAPS.clear()
        QFontDatabase.removeAllApplicationFonts()

    @classmethod
    def _key2family(cls, key: str) -> tuple[str, str]:
        """Return (family, style) given a font `key`."""
        key = key.split(".", maxsplit=1)[0]
        if key not in cls._LOADED_KEYS:
            from . import _plugins

            try:
                font_cls = _plugins.get_font_class(key)
                result = cls.addFont(
                    font_cls.__font_file__, key, charmap=dict(font_cls.__dict__)
                )
                if not result:  # pragma: no cover
                    raise Exception("Invalid font file")
                cls._LOADED_KEYS[key] = result
            except ValueError as e:
                raise ValueError(
                    f"Unrecognized font key: {key!r}.\n"
                    f"Known plugin keys include: {_plugins.available()}.\n"
                    f"Loaded keys include: {list(cls._LOADED_KEYS)}."
                ) from e
        return cls._LOADED_KEYS[key]

    @classmethod
    def _ensure_char(cls, char: str, family: str, style: str) -> str:
        """Make sure that `char` is a glyph provided by `family` and `style`."""
        if len(char) == 1 and ord(char) > 256:
            return char
        try:
            charmap = cls._CHARMAPS[(family, style)]
        except KeyError as e:
            raise KeyError(
                f"No charmap registered for font '{family} ({style})'"
            ) from e
        if char in charmap:
            # split in case the charmap includes the key
            return charmap[char].split(".", maxsplit=1)[-1]

        ident = _ensure_identifier(char)
        if ident in charmap:
            return charmap[ident].split(".", maxsplit=1)[-1]

        ident = f"{char!r} or {ident!r}" if char != ident else repr(ident)
        raise ValueError(f"Font '{family} ({style})' has no glyph with the key {ident}")

    @classmethod
    def key2glyph(cls, glyph_key: str) -> tuple[str, str, str | None]:
        """Return (char, family, style) given a `glyph_key`."""
        if "." not in glyph_key:
            raise ValueError("Glyph key must contain a period")
        font_key, char = glyph_key.split(".", maxsplit=1)
        family, style = cls._key2family(font_key)
        char = cls._ensure_char(char, family, style)
        return char, family, style

    @classmethod
    def addFont(
        cls, filepath: str, prefix: str, charmap: dict[str, str] | None = None
    ) -> tuple[str, str] | None:
        r"""Add font at `filepath` to the registry under `key`.

        If you'd like to later use a fontkey in the form of `key.some-name`, then
        `charmap` must be provided and provide a mapping for all of the glyph names
        to their unicode numbers. If a charmap is not provided, glyphs must be directly
        accessed with their unicode as something like `key.\\uffff`.

        Parameters
        ----------
        filepath : str
            Path to an OTF or TTF file containing the fonts
        prefix : str
            A key that will represent this font file when used for lookup.  For example,
            'fa5s' for 'Font-Awesome 5 Solid'.
        charmap : Dict[str, str], optional
            optional mapping for all of the glyph names to their unicode numbers.
            See note above.

        Returns
        -------
        Tuple[str, str], optional
            font-family and font-style for the file just registered, or None if
            something goes wrong.
        """
        if prefix in cls._LOADED_KEYS:
            warnings.warn(f"Prefix {prefix} already loaded", stacklevel=2)
            return None

        if not Path(filepath).exists():
            raise FileNotFoundError(f"Font file doesn't exist: {filepath}")
        if QApplication.instance() is None:
            raise RuntimeError("Please create QApplication before adding a Font")

        fontId = QFontDatabase.addApplicationFont(str(Path(filepath).absolute()))
        if fontId < 0:  # pragma: no cover
            warnings.warn(f"Cannot load font file: {filepath}", stacklevel=2)
            return None

        families = QFontDatabase.applicationFontFamilies(fontId)
        if not families:  # pragma: no cover
            warnings.warn(f"Font file is empty!: {filepath}", stacklevel=2)
            return None
        family: str = families[0]

        # in Qt6, everything becomes a static member
        QFd: QFontDatabase | type[QFontDatabase] = (
            QFontDatabase()
            if tuple(cast(str, QT_VERSION).split(".")) < ("6", "0")
            else QFontDatabase
        )

        styles = QFd.styles(family)
        style: str = styles[-1] if styles else ""
        if not QFd.isSmoothlyScalable(family, style):  # pragma: no cover
            warnings.warn(
                f"Registered font {family} ({style}) is not smoothly scalable. "
                "Icons may not look attractive.",
                stacklevel=2,
            )

        cls._LOADED_KEYS[prefix] = (family, style)
        if charmap:
            cls._CHARMAPS[(family, style)] = charmap
        return (family, style)

    def icon(
        self,
        glyph_key: str,
        *,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: ValidColor | None = None,
        opacity: float = 1,
        animation: Animation | None = None,
        transform: QTransform | None = None,
        states: dict[str, IconOptionDict | IconOpts] | None = None,
    ) -> QFontIcon:
        self.key2glyph(glyph_key)  # make sure it's a valid glyph_key
        default_opts = _IconOptions(
            glyph_key=glyph_key,
            scale_factor=scale_factor,
            color=color,
            opacity=opacity,
            animation=animation,
            transform=transform,
        )
        icon = QFontIcon(default_opts)
        for kw, options in (states or {}).items():
            if isinstance(options, IconOpts):
                options = default_opts._update(options).dict()
            icon.addState(*_norm_state_mode(kw), **options)
        return icon

    def setTextIcon(
        self, widget: QWidget, glyph_key: str, size: float | None = None
    ) -> None:
        """Sets text on a widget to a specific font & glyph.

        This is an alternative to setting a `QIcon` with a pixmap.  It may
        be easier to combine with dynamic stylesheets.
        """
        setText = getattr(widget, "setText", None)
        if not setText:  # pragma: no cover
            raise TypeError(f"Object does not a setText method: {widget}")

        glyph = self.key2glyph(glyph_key)[0]
        size = size or DEFAULT_SCALING_FACTOR
        size = size if size > 1 else widget.height() * size
        widget.setFont(self.font(glyph_key, int(size)))
        setText(glyph)

    def font(self, font_prefix: str, size: int | None = None) -> QFont:
        """Create QFont for `font_prefix`."""
        font_key, _ = font_prefix.split(".", maxsplit=1)
        family, style = self._key2family(font_key)
        font = QFont()
        font.setFamily(family)
        if style:
            font.setStyleName(style)
        if size:
            font.setPixelSize(int(size))
        return font


def _ensure_identifier(name: str) -> str:
    """Normalize string to valid identifier."""
    import keyword

    if not name:
        return ""

    # add _ to beginning of names starting with numbers
    if name[0].isdigit():
        name = f"_{name}"

    # add _ to end of reserved keywords
    if keyword.iskeyword(name):
        name += "_"

    # replace dashes and spaces with underscores
    name = name.replace("-", "_").replace(" ", "_")

    if not str.isidentifier(name):
        raise ValueError(f"Could not canonicalize name: {name!r}. (not an identifier)")
    return name
