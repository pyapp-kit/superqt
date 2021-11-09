from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import DefaultDict, Dict, FrozenSet, Optional, Tuple, Type, Union, cast

from typing_extensions import TypedDict

from superqt.qtcompat import QT_VERSION
from superqt.qtcompat.QtCore import QObject, QPoint, QRect, QSize, Qt
from superqt.qtcompat.QtGui import (
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
from superqt.qtcompat.QtWidgets import QApplication, QStyleOption, QWidget

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
    Tuple[int, int, int, int],
    Tuple[int, int, int],
    None,
]
_DEFAULT_STATE = (QIcon.State.Off, QIcon.Mode.Normal)
_states: Dict[FrozenSet[str], tuple[QIcon.State, QIcon.Mode]] = {
    frozenset({"on"}): (QIcon.State.On, QIcon.Mode.Normal),
    frozenset({"off"}): _DEFAULT_STATE,
    frozenset({"normal"}): _DEFAULT_STATE,
    frozenset({"active"}): (QIcon.State.Off, QIcon.Mode.Active),
    frozenset({"selected"}): (QIcon.State.Off, QIcon.Mode.Selected),
    frozenset({"disabled"}): (QIcon.State.Off, QIcon.Mode.Disabled),
    frozenset({"on", "normal"}): (QIcon.State.On, QIcon.Mode.Normal),
    frozenset({"on", "active"}): (QIcon.State.On, QIcon.Mode.Active),
    frozenset({"on", "selected"}): (QIcon.State.On, QIcon.Mode.Selected),
    frozenset({"on", "disabled"}): (QIcon.State.On, QIcon.Mode.Disabled),
    frozenset({"off", "normal"}): _DEFAULT_STATE,
    frozenset({"off", "active"}): (QIcon.State.Off, QIcon.Mode.Active),
    frozenset({"off", "selected"}): (QIcon.State.Off, QIcon.Mode.Selected),
    frozenset({"off", "disabled"}): (QIcon.State.Off, QIcon.Mode.Disabled),
}


class IconStateMode(Enum):
    ON_NORMAL = (QIcon.State.On, QIcon.Mode.Normal)
    ON_ACTIVE = (QIcon.State.On, QIcon.Mode.Active)
    ON_SELECTED = (QIcon.State.On, QIcon.Mode.Selected)
    ON_DISABLED = (QIcon.State.On, QIcon.Mode.Disabled)
    OFF_NORMAL = (QIcon.State.Off, QIcon.Mode.Normal)
    OFF_ACTIVE = (QIcon.State.Off, QIcon.Mode.Active)
    OFF_SELECTED = (QIcon.State.Off, QIcon.Mode.Selected)
    OFF_DISABLED = (QIcon.State.Off, QIcon.Mode.Disabled)
    ON = ON_NORMAL
    OFF = OFF_NORMAL
    NORMAL = OFF_NORMAL
    ACTIVE = OFF_ACTIVE
    SELECTED = OFF_SELECTED
    DEFAULT = OFF_NORMAL


def _norm_state_mode(kw: str) -> Tuple[QIcon.State, QIcon.Mode]:
    try:
        return _states[frozenset(kw.lower().split("_"))]
    except KeyError:
        raise ValueError(
            f"{kw!r} is not a valid state key, must be a combination of {{on, "
            "off, active, disabled, selected, normal} separated by underscore"
        )


class IconOptionDict(TypedDict, total=False):
    glyph_key: str
    scale_factor: float
    color: ValidColor
    opacity: float
    animation: Optional[Animation]
    transform: Optional[QTransform]


# public facing, for a nicer IDE experience than a dict
@dataclass
class IconOpts:
    glyph_key: Union[str, Unset] = _Unset
    scale_factor: Union[float, Unset] = _Unset
    color: Union[ValidColor, Unset] = _Unset
    opacity: Union[float, Unset] = _Unset
    animation: Union[Animation, Unset, None] = _Unset
    transform: Union[QTransform, Unset, None] = _Unset

    def dict(self) -> IconOptionDict:
        # not using asdict due to pickle errors on animation
        d = {k: v for k, v in vars(self).items() if v is not _Unset}
        return cast(IconOptionDict, d)


@dataclass
class IconOptions:
    """The set of options needed to render a font in a single State/Mode."""

    glyph_key: str
    scale_factor: float = DEFAULT_SCALING_FACTOR
    color: ValidColor = None
    opacity: float = DEFAULT_OPACITY
    animation: Optional[Animation] = None
    transform: Optional[QTransform] = None

    def _update(self, icon_opts: IconOpts) -> IconOptions:
        return IconOptions(**{**vars(self), **icon_opts.dict()})

    def dict(self) -> IconOptionDict:
        # not using asdict due to pickle errors on animation
        return cast(IconOptionDict, vars(self))


class _QFontIconEngine(QIconEngine):
    _opt_hash: str = ""

    def __init__(self, options: IconOptions):
        super().__init__()
        self._opts: DefaultDict[
            QIcon.State, Dict[QIcon.Mode, Optional[IconOptions]]
        ] = DefaultDict(dict)
        self._opts[QIcon.State.Off][QIcon.Mode.Normal] = options
        self.update_hash()

    @property
    def _default_opts(self) -> IconOptions:
        return cast(IconOptions, self._opts[QIcon.State.Off][QIcon.Mode.Normal])

    def _add_opts(self, state: QIcon.State, mode: QIcon.Mode, opts: IconOpts) -> None:
        self._opts[state][mode] = self._default_opts._update(opts)
        self.update_hash()

    def clone(self) -> QIconEngine:  # pragma: no cover
        ico = _QFontIconEngine(self._default_opts)
        ico._opts = self._opts.copy()
        return ico

    def _get_opts(self, state: QIcon.State, mode: QIcon.Mode) -> IconOptions:
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
        font.setFamily(family)  # set sepeartely for Qt6
        font.setPixelSize(round(rect.height() * opts.scale_factor))
        if style:
            font.setStyleName(style)

        # color
        color_args = opts.color if isinstance(opts.color, tuple) else (opts.color,)

        # animation
        if opts.animation is not None:
            opts.animation.animate(painter, rect)

        # animation
        if opts.transform is not None:
            painter.setTransform(opts.transform, True)

        painter.save()
        painter.setPen(QColor(*color_args))
        painter.setOpacity(opts.opacity)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        # first look in cache
        pmckey = self._pmcKey(size, mode, state)
        # pm = QPixmapCache.find(pmckey)
        # if pm:
        #     print("cache hit", pmckey, mode, state)
        #     return pm
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

        if not pixmap.isNull():
            QPixmapCache.insert(pmckey, pixmap)

        return pixmap

    def _pmcKey(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> str:
        k = ((((((size.width()) << 11) | size.height()) << 11) | mode) << 4) | state
        return f"$superqt_{self._opt_hash}_{hex(k)}"

    def update_hash(self) -> None:
        hsh = id(self)
        for state, d in self._opts.items():
            for mode, opts in d.items():
                if not opts:
                    continue
                hsh += hash(hash(opts.glyph_key) + hash(opts.color) + state + mode)
        self._opt_hash = hex(hsh)


class QFontIcon(QIcon):
    def __init__(self, options: IconOptions) -> None:
        self._engine = _QFontIconEngine(options)
        super().__init__(self._engine)

    def addState(
        self,
        state: QIcon.State = QIcon.State.Off,
        mode: QIcon.Mode = QIcon.Mode.Normal,
        glyph_key: Union[str, Unset] = _Unset,
        scale_factor: Union[float, Unset] = _Unset,
        color: Union[ValidColor, Unset] = _Unset,
        opacity: Union[float, Unset] = _Unset,
        animation: Union[Animation, Unset, None] = _Unset,
        transform: Union[QTransform, Unset, None] = _Unset,
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
    _LOADED_KEYS: Dict[str, Tuple[str, Optional[str]]] = dict()

    # map of (font_family, font_style) -> character (char may include key)
    _CHARMAPS: Dict[Tuple[str, Optional[str]], Dict[str, str]] = dict()

    # singleton instance, use `instance()` to retrieve
    __instance: Optional[QFontIconStore] = None

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        # QT6 drops this
        dpi = getattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps", None)
        if dpi:
            QApplication.setAttribute(dpi)

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
    def _key2family(cls, key: str) -> Tuple[str, Optional[str]]:
        """Return (family, style) given a font `key`"""
        key = key.split(".", maxsplit=1)[0]
        if key not in cls._LOADED_KEYS:
            from . import _plugins

            try:
                font_cls = _plugins.get_font_class(key)
                result = cls.addFont(
                    font_cls.__font_file__, key, charmap=font_cls.__dict__
                )
                if not result:  # pragma: no cover
                    raise Exception("Invalid font file")
                cls._LOADED_KEYS[key] = result
            except Exception as e:
                raise ValueError(
                    f"Unrecognized font key: {key!r}.\n"
                    f"Known plugin keys include: {_plugins.available()}.\n"
                    f"Loaded keys include: {list(cls._LOADED_KEYS)}."
                ) from e
        return cls._LOADED_KEYS[key]

    @classmethod
    def _ensure_char(cls, char: str, family: str, style: str) -> str:
        """make sure that `char` is a glyph provided by `family` and `style`."""
        if len(char) == 1 and ord(char) > 256:
            return char
        try:
            charmap = cls._CHARMAPS[(family, style)]
        except KeyError:
            raise KeyError(f"No charmap registered for font '{family} ({style})'")
        if char in charmap:
            # split in case the charmap includes the key
            return charmap[char].split(".", maxsplit=1)[-1]

        ident = _ensure_identifier(char)
        if ident in charmap:
            return charmap[ident].split(".", maxsplit=1)[-1]

        ident = f"{char!r} or {ident!r}" if char != ident else repr(ident)
        raise ValueError(f"Font '{family} ({style})' has no glyph with the key {ident}")

    @classmethod
    def key2glyph(cls, glyph_key: str) -> tuple[str, str, Optional[str]]:
        """Return (char, family, style) given a `glyph_key`"""
        if "." not in glyph_key:
            raise ValueError("Glyph key must contain a period")
        font_key, char = glyph_key.split(".", maxsplit=1)
        family, style = cls._key2family(font_key)
        char = cls._ensure_char(char, family, style)
        return char, family, style

    @classmethod
    def addFont(
        cls, filepath: str, prefix: str, charmap: Optional[Dict[str, str]] = None
    ) -> Optional[Tuple[str, str]]:
        """Add font at `filepath` to the registry under `key`.

        If you'd like to later use a fontkey in the form of `key.some-name`, then
        `charmap` must be provided and provide a mapping for all of the glyph names
        to their unicode numbers. If a charmap is not provided, glyphs must be directly
        accessed with their unicode as something like `key.\uffff`.

        Parameters
        ----------
        filepath : str
            Path to an OTF or TTF file containing the fonts
        key : str
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
        assert prefix not in cls._LOADED_KEYS, f"Prefix {prefix} already loaded"
        assert Path(filepath).exists(), f"Font file doesn't exist: {filepath}"
        assert QApplication.instance() is not None, "Please create QApplication first."
        # TODO: remember filepath?

        fontId = QFontDatabase.addApplicationFont(str(Path(filepath).absolute()))
        if fontId < 0:  # pragma: no cover
            warnings.warn(f"Cannot load font file: {filepath}")
            return None

        families = QFontDatabase.applicationFontFamilies(fontId)
        if not families:  # pragma: no cover
            warnings.warn(f"Font file is empty!: {filepath}")
            return None
        family: str = families[0]

        # in Qt6, everything becomes a static member
        QFd: Union[QFontDatabase, Type[QFontDatabase]] = (
            QFontDatabase()  # type: ignore
            if tuple(QT_VERSION.split(".")) < ("6", "0")
            else QFontDatabase
        )

        styles = QFd.styles(family)  # type: ignore
        style: str = styles[-1] if styles else ""
        if not QFd.isSmoothlyScalable(family, style):  # pragma: no cover
            warnings.warn(
                f"Registered font {family} ({style}) is not smoothly scalable. "
                "Icons may not look attractive."
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
        color: ValidColor = None,
        opacity: float = 1,
        animation: Optional[Animation] = None,
        transform: Optional[QTransform] = None,
        states: Dict[str, Union[IconOptionDict, IconOpts]] = {},
    ) -> QFontIcon:
        self.key2glyph(glyph_key)  # make sure it's a valid glyph_key
        default_opts = IconOptions(
            glyph_key=glyph_key,
            scale_factor=scale_factor,
            color=color,
            opacity=opacity,
            animation=animation,
            transform=transform,
        )
        icon = QFontIcon(default_opts)
        for kw, options in states.items():
            if isinstance(options, IconOpts):
                options = default_opts._update(options).dict()
            icon.addState(*_norm_state_mode(kw), **options)
        return icon

    def setTextIcon(
        self, widget: QWidget, glyph_key: str, size: Optional[float] = None
    ) -> None:
        """Sets text on a widget to a specific font & glyph.

        This is an alternative to setting a QIcon with a pixmap.  It may
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

    def font(self, font_prefix: str, size: Optional[int] = None) -> QFont:
        """Create QFont for `font_prefix`"""
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
    """Normalize string to valid identifier"""
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

    assert str.isidentifier(name), f"Could not canonicalize name: {name}"
    return name
