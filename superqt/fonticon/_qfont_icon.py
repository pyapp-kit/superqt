from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum, EnumMeta
from importlib.metadata import EntryPoint
from pathlib import Path
from typing import TYPE_CHECKING, DefaultDict, Tuple, Type, Union

from superqt.qtcompat import QT_VERSION
from superqt.qtcompat.QtCore import QObject, QPoint, QRect, QSize, Qt
from superqt.qtcompat.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QIconEngine,
    QPainter,
    QPalette,
    QPixmap,
    QTransform,
)
from superqt.qtcompat.QtWidgets import QApplication, QWidget

try:
    from importlib.metadata import EntryPoint, entry_points
except ImportError:
    from importlib_metadata import entry_points, EntryPoint  # type: ignore

from ._animations import Animation
from ._utils import is_font_enum_type, str2enum

if TYPE_CHECKING:
    from ._utils import FontEnum

    FontEnumType = Type[FontEnum]
    GlyphKey = Union[str, FontEnum]


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
Unset = object()
_DEFAULT_STATE = (QIcon.State.Off, QIcon.Mode.Normal)
_states: dict[frozenset, tuple[QIcon.State, QIcon.Mode]] = {
    frozenset(["on"]): (QIcon.State.On, QIcon.Mode.Normal),
    frozenset(["off"]): _DEFAULT_STATE,
    frozenset(["normal"]): _DEFAULT_STATE,
    frozenset(["active"]): (QIcon.State.Off, QIcon.Mode.Active),
    frozenset(["selected"]): (QIcon.State.Off, QIcon.Mode.Selected),
    frozenset(["disabled"]): (QIcon.State.Off, QIcon.Mode.Disabled),
    frozenset(["on", "normal"]): (QIcon.State.On, QIcon.Mode.Normal),
    frozenset(["on", "active"]): (QIcon.State.On, QIcon.Mode.Active),
    frozenset(["on", "selected"]): (QIcon.State.On, QIcon.Mode.Selected),
    frozenset(["on", "disabled"]): (QIcon.State.On, QIcon.Mode.Disabled),
    frozenset(["off", "normal"]): _DEFAULT_STATE,
    frozenset(["off", "active"]): (QIcon.State.Off, QIcon.Mode.Active),
    frozenset(["off", "selected"]): (QIcon.State.Off, QIcon.Mode.Selected),
    frozenset(["off", "disabled"]): (QIcon.State.Off, QIcon.Mode.Disabled),
}


@dataclass
class IconOptions:
    """The set of options needed to render a font in a single State/Mode."""

    glyph: GlyphKey
    scale_factor: float = DEFAULT_SCALING_FACTOR
    color: ValidColor = None
    opacity: float = DEFAULT_OPACITY
    animation: Animation | None = None
    transform: QTransform | None = None

    @classmethod
    def _from_kwargs(
        cls, kwargs: dict, defaults: IconOptions | None = None
    ) -> IconOptions:
        kwargs = {
            f: getattr(defaults, f) if kwargs[f] is Unset else kwargs[f]
            for f in IconOptions.__dataclass_fields__  # type: ignore
        }
        return IconOptions(**kwargs)


def key2glyph(glyph: GlyphKey) -> tuple[str, str, str | None]:
    """Return char, family, style given a GlyphKey"""
    if isinstance(glyph, str):
        font_key, char = glyph.split(".")
        family, style = QFontIconStore._key2family(font_key)
    elif isinstance(glyph, Enum):
        family, style = QFontIconStore._key2family(glyph)
        char = glyph.value
    return char, family, style


class _QFontIconEngine(QIconEngine):
    def __init__(self, options: IconOptions):
        super().__init__()
        self._default_opts = options
        self._opts: DefaultDict[
            QIcon.State, dict[QIcon.Mode, IconOptions | None]
        ] = DefaultDict(dict)

    def clone(self) -> QIconEngine:
        ico = _QFontIconEngine(None)  # type: ignore
        ico._opts = self._opts.copy()
        return ico

    def _get_opts(self, state, mode: QIcon.Mode) -> IconOptions:
        opts = self._opts[state].get(mode) or self._default_opts
        if opts.color is None:
            # use current palette in absense of color
            role = {
                QIcon.Mode.Disabled: QPalette.ColorGroup.Disabled,
                QIcon.Mode.Selected: QPalette.ColorGroup.Current,
                QIcon.Mode.Normal: QPalette.ColorGroup.Normal,
                QIcon.Mode.Active: QPalette.ColorGroup.Active,
            }
            opts.color = QApplication.palette().color(role[mode], QPalette.ButtonText)
        return opts

    def paint(
        self,
        painter: QPainter,
        rect: QRect,
        mode: QIcon.Mode,
        state: QIcon.State,
    ) -> None:
        opts = self._get_opts(state, mode)

        char, family, style = key2glyph(opts.glyph)

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

        painter.save()
        painter.setPen(QColor(*color_args))
        painter.setOpacity(opts.opacity)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, char)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        return pixmap


class QFontIcon(QIcon):
    def __init__(self, options):
        self._engine = _QFontIconEngine(options)
        super().__init__(self._engine)

    def addState(
        self,
        state: QIcon.State = QIcon.State.Off,
        mode: QIcon.Mode = QIcon.Mode.Normal,
        glyph: str | None = None,
        font_family: str | None = None,
        font_style: str | None = None,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: ValidColor = None,
        opacity: float = DEFAULT_OPACITY,
        animation: Animation | None = None,
        transform: QTransform | None = None,
    ):
        """Set icon options for a specific mode/state."""
        opts = IconOptions._from_kwargs(locals(), self._engine._default_opts)
        self._engine._opts[state][mode] = opts


class QFontIconStore(QObject):
    ENTRY_POINT = "superqt.fonticon"
    _FONT_LIBRARY: dict[str, EnumMeta] = {}
    _PLUGIN_KEYS: dict[str, EntryPoint] = {}

    # map of key -> (font_family, font_style)
    _LOADED_KEYS: dict[str, tuple[str, str | None]] = dict()
    # map of FontEnumType -> (font_family, font_style)
    _LOADED_ENUMS: dict[FontEnumType, tuple[str, str | None]] = dict()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent=parent)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        self._registered_fonts: DefaultDict[str, set[str]] = DefaultDict(set)
        self._registered_enums: dict[EnumMeta, tuple[int, str, list[str]]] = dict()

    @classmethod
    def _key2family(cls, key: GlyphKey) -> tuple[str, str | None]:
        """Return (family, style) given a font key"""

        if isinstance(key, str):
            if key in cls._LOADED_KEYS:
                return cls._LOADED_KEYS[key]
        else:
            enum_type = type(key) if isinstance(key, Enum) else key
            if enum_type in cls._LOADED_ENUMS:
                return cls._LOADED_ENUMS[enum_type]
            assert isinstance(enum_type, EnumMeta)

            # we have an unloaded enum
            # see if it comes from a plugin
            for _key, ep in cls._PLUGIN_KEYS.items():
                if ep.value == f"{enum_type.__module__}:{enum_type.__name__}":
                    key = _key
                    break

        cls._try_load_plugin(key)

        try:
            return cls._LOADED_KEYS[key]
        except KeyError:
            raise ValueError(
                f"Unrecognized font key: {key}.\n"
                f"Known plugin keys include: {list(cls._PLUGIN_KEYS)}.\n"
                f"Loaded keys include: {list(cls._LOADED_KEYS)}."
                f"Loaded enums include: {list(cls._LOADED_ENUMS)}."
            )

    @classmethod
    def _try_load_plugin(cls, key: str) -> tuple[str, str | None] | None:
        if key not in cls._PLUGIN_KEYS:
            cls._discover_fonts()

        if key not in cls._PLUGIN_KEYS:
            return None

        ep = cls._PLUGIN_KEYS[key]
        font_enum: FontEnumType = ep.load()

        if not is_font_enum_type(font_enum):
            warnings.warn(
                f"Object {cls} loaded from plugin {ep.value!r} is not a valid font enum"
            )
            # TODO: pop key from _PLUGIN_KEYS and block future discovery
            return None

        filepath = font_enum._font_file()
        loaded = cls.addFont(filepath, key)
        if loaded:
            cls._LOADED_ENUMS[font_enum] = loaded
            return loaded
        return None

    @classmethod
    def addFont(cls, filepath: str, key: str) -> tuple[str, str] | None:
        """Add font at `filepath` to registry under `key`."""
        assert key not in cls._LOADED_KEYS, f"Key {key} already loaded"
        assert Path(filepath).exists(), f"Font file doesn't exist: {filepath}"
        # TODO: remember filepath?

        fontId = QFontDatabase.addApplicationFont(str(Path(filepath).absolute()))
        if fontId < 0:
            warnings.warn(f"Cannot load font file: {filepath}")
            return None

        families = QFontDatabase.applicationFontFamilies(fontId)
        if not families:
            warnings.warn(f"Font file is empty!: {filepath}")
            return None
        family = families[0]

        # in Qt6, everything becomes a static member
        QFd: QFontDatabase | type[QFontDatabase] = (
            QFontDatabase()
            if tuple(QT_VERSION.split(".")) < ("6", "0")
            else QFontDatabase
        )

        styles = QFd.styles(family)  # type: ignore
        style = styles[-1] if styles else None
        if not QFd.isSmoothlyScalable(family, style):
            warnings.warn(
                f"Registered font {family} ({style}) is not smoothly scalable. "
                "Icons may not look attractive."
            )

        cls._LOADED_KEYS[key] = (family, style)
        return (family, style)

    def icon(
        self,
        glyph: GlyphKey,
        *,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: ValidColor = None,
        opacity: float = 1,
        animation: Animation | None = None,
        transform: QTransform | None = None,
        states: dict[str, dict] = {},
    ) -> QFontIcon:
        default_opts = IconOptions(
            glyph, scale_factor, color, opacity, animation, transform
        )

        icon = QFontIcon(default_opts)
        for kw, options in states.items():
            try:
                state, mode = _states[frozenset(kw.lower().split("_"))]
            except KeyError:
                raise ValueError(
                    f"{kw!r} is not a valid state key, must be a combination of {{on, "
                    "off, active, disabled, selected, normal} separated by underscore"
                )
            icon.addState(state, mode, **options)
        return icon

    def setTextIcon(self, wdg: QWidget, key, size=None) -> None:
        """Sets text on a widget to a specific font & glyph.

        This is an alternative to setting a QIcon with a pixmap.  It may
        be easier to combine with dynamic stylesheets.
        """
        if not hasattr(wdg, "setText"):
            raise TypeError(f"Object does not a setText method: {wdg}")

        family, style, glyph = self._get_family_and_glpyh(key)
        font = QFont()
        font.setFamily(family)
        if style:
            font.setStyleName(style)
        size = size or DEFAULT_SCALING_FACTOR
        font.setPixelSize(size if size > 1 else wdg.height() * size)
        wdg.setFont(font)
        wdg.setText(glyph)

    def _get_family_and_glpyh(self, glyph: GlyphKey):
        enum = str2enum(glyph) if isinstance(glyph, str) else glyph
        if not is_font_enum_type(type(enum)):
            raise TypeError(f"{enum} must be a string (icon key) or a FontEnum member")
        glyph = enum.value
        fontenum = type(enum)

        if fontenum not in self._registered_enums:
            self.addFont(fontenum)
        _, family, styles = self._registered_enums[fontenum]
        style = styles[0]
        return family, style, glyph

    def font(self, family, style: str = None, size: int = None) -> QFont:
        raise NotImplementedError()
        # if is_font_enum_type(type(family)) or is_font_enum_type(family):
        #     if family not in self:
        #         self.addFont(family)
        #     style = family._font_style()
        #     _family = family._font_family()
        # else:
        #     _family = family

        # font = QFont()
        # font.setFamily(_family)
        # if style:
        #     font.setStyleName(style)
        # if size:
        #     font.setPixelSize(size)
        # return font

    def registeredFonts(self) -> dict[str, set[str]]:
        """Return registered font list (family and styles)."""
        return dict(self._registered_fonts)

    # def isRegistered(self, font_family: StringOrEnum) -> bool:
    #     """Return `True` if `font_family` is registered."""
    #     return font_family in self

    # def __contains__(self, font: StringOrEnum) -> bool:
    #     if isinstance(font, str):
    #         return any(font.lower() == key.lower() for key in self._registered_fonts)
    #     return ensure_font_enum_type(font) in self._registered_enums

    @classmethod
    def _discover_fonts(cls):
        print("discovert")

        for ep in entry_points().get(cls.ENTRY_POINT, {}):
            print("ep", ep)
            cls._PLUGIN_KEYS[ep.name] = ep
