from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Dict, Optional, Tuple, Type, Union

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

from ._animations import Animation

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
_states: Dict[frozenset, tuple[QIcon.State, QIcon.Mode]] = {
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

    glyph: str
    scale_factor: float = DEFAULT_SCALING_FACTOR
    color: ValidColor = None
    opacity: float = DEFAULT_OPACITY
    animation: Optional[Animation] = None
    transform: Optional[QTransform] = None

    @classmethod
    def _from_kwargs(
        cls, kwargs: dict, defaults: Optional[IconOptions] = None
    ) -> IconOptions:
        defaults = defaults or _DEFAULT_ICON_OPTS
        kwargs = {
            f: getattr(defaults, f) if kwargs[f] is None else kwargs[f]
            for f in IconOptions.__dataclass_fields__  # type: ignore
        }
        return IconOptions(**kwargs)


_DEFAULT_ICON_OPTS = IconOptions("")


class _QFontIconEngine(QIconEngine):
    def __init__(self, options: IconOptions):
        super().__init__()
        self._default_opts = options
        self._opts: DefaultDict[
            QIcon.State, Dict[QIcon.Mode, Optional[IconOptions]]
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

        char, family, style = QFontIconStore.key2glyph(opts.glyph)

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
        painter.drawText(rect, Qt.AlignCenter, char)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
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
        glyph: Optional[str] = None,
        font_family: Optional[str] = None,
        font_style: Optional[str] = None,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: ValidColor = None,
        opacity: float = DEFAULT_OPACITY,
        animation: Optional[Animation] = None,
        transform: Optional[QTransform] = None,
    ):
        """Set icon options for a specific mode/state."""
        opts = IconOptions._from_kwargs(locals(), self._engine._default_opts)
        self._engine._opts[state][mode] = opts


class QFontIconStore(QObject):

    # map of key -> (font_family, font_style)
    _LOADED_KEYS: Dict[str, Tuple[str, Optional[str]]] = dict()
    # map of (font_family, font_style) -> character (char may include key)
    _CHARMAPS: Dict[Tuple[str, Optional[str]], Dict[str, str]] = dict()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    @classmethod
    def _key2family(cls, key: str) -> Tuple[str, Optional[str]]:
        """Return (family, style) given a font key"""
        key = key.split(".", maxsplit=1)[0]
        if key not in cls._LOADED_KEYS:
            from . import _plugins

            try:
                font_cls = _plugins.get_font_class(key)
                result = cls.addFont(
                    font_cls.__font_file__, key, charmap=font_cls.__dict__
                )
                if not result:
                    raise Exception("Invalid font file")
                cls._LOADED_KEYS[key] = result
            except Exception as e:
                raise ValueError(
                    f"Unrecognized font key: {key}.\n"
                    f"Known plugin keys include: {_plugins.available()}.\n"
                    f"Loaded keys include: {list(cls._LOADED_KEYS)}."
                ) from e
        return cls._LOADED_KEYS[key]

    @classmethod
    def _ensure_char(cls, char, family, style) -> str:
        """make sure that char is provided by family and style."""
        if len(char) == 1 and ord(char) > 256:
            return char
        try:
            charmap = cls._CHARMAPS[(family, style)]
        except KeyError:
            raise KeyError(f"No charmap registered for {family} ({style})")
        if char in charmap:
            # in case the charmap includes the key
            return charmap[char].split(".", maxsplit=1)[-1]

        from ._utils import ensure_identifier

        ident = ensure_identifier(char)
        if ident in charmap:
            return charmap[ident].split(".", maxsplit=1)[-1]

        ident = f"{char!r} or {ident!r}" if char != ident else repr(ident)
        raise ValueError(f"{family} ({style}) has no char with the key {ident}")

    @classmethod
    def key2glyph(cls, glyph: str) -> tuple[str, str, Optional[str]]:
        """Return char, family, style given a GlyphKey"""
        font_key, char = glyph.split(".", maxsplit=1)
        family, style = cls._key2family(font_key)
        char = cls._ensure_char(char, family, style)
        return char, family, style

    @classmethod
    def addFont(
        cls, filepath: str, key: str, charmap=None
    ) -> Optional[Tuple[str, str]]:
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
        family: str = families[0]

        # in Qt6, everything becomes a static member
        QFd: Union[QFontDatabase, Type[QFontDatabase]] = (
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
        if charmap:
            cls._CHARMAPS[(family, style)] = charmap
        return (family, style)

    def icon(
        self,
        glyph: str,
        *,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: ValidColor = None,
        opacity: float = 1,
        animation: Optional[Animation] = None,
        transform: Optional[QTransform] = None,
        states: Dict[str, dict] = {},
    ) -> QFontIcon:
        default_opts = IconOptions._from_kwargs(locals())

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

        glyph, family, style = self.key2glyph(key)

        font = QFont()
        font.setFamily(family)
        if style:
            font.setStyleName(style)
        size = size or DEFAULT_SCALING_FACTOR
        font.setPixelSize(size if size > 1 else wdg.height() * size)
        wdg.setFont(font)
        wdg.setText(glyph)

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

    def registeredFonts(self) -> Dict[str, set[str]]:
        """Return registered font list (family and styles)."""
        return dict(self._registered_fonts)

    # def isRegistered(self, font_family: StringOrEnum) -> bool:
    #     """Return `True` if `font_family` is registered."""
    #     return font_family in self

    # def __contains__(self, font: StringOrEnum) -> bool:
    #     if isinstance(font, str):
    #         return any(font.lower() == key.lower() for key in self._registered_fonts)
    #     return ensure_font_enum_type(font) in self._registered_enums
