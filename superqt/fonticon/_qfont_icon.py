import warnings
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Optional, Set, Tuple, Type, Union

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
from ._utils import (
    ensure_font_enum_type,
    is_font_enum_member,
    is_font_enum_type,
    str2enum,
)

# A 16 pixel-high icon yields a font size of 14, which is pixel perfect
# for font-awesome. 16 * 0.875 = 14
# The reason why the glyph size is smaller than the icon size is to
# account for font bearing.
DEFAULT_SCALING_FACTOR = 0.875
StringOrEnum = Union[str, Type[Enum]]


@dataclass
class IconOptions:
    glyph: str
    font_family: str
    font_style: Optional[str] = None
    scale_factor: float = DEFAULT_SCALING_FACTOR
    color: Union[
        QColor,
        int,
        str,
        Qt.GlobalColor,
        Tuple[int, int, int, int],
        Tuple[int, int, int],
        None,
    ] = None
    opacity: float = 1
    animation: Optional[Animation] = None
    transform: Optional[QTransform] = None


valid_options = [
    "on_normal",  # == "normal" == "on"
    "on_active",  # == "active"
    "on_selected",  # == "selected"
    "on_disabled",  # == "disabled"
    "off_normal",  # == "off"
    "off_active",
    "off_selected",
    "off_disabled",
]


class _QFontIconEngine(QIconEngine):
    def __init__(self, options: IconOptions):
        super().__init__()
        self._default_opts = options
        self._opts: Dict[QIcon.State, Dict[QIcon.Mode, Optional[IconOptions]]] = {
            QIcon.State.On: {
                QIcon.Mode.Normal: None,
                QIcon.Mode.Disabled: None,
                QIcon.Mode.Active: None,
                QIcon.Mode.Selected: None,
            },
            QIcon.State.Off: {
                QIcon.Mode.Normal: None,
                QIcon.Mode.Disabled: None,
                QIcon.Mode.Active: None,
                QIcon.Mode.Selected: None,
            },
        }

    def clone(self) -> QIconEngine:
        ico = _QFontIconEngine(None)  # type: ignore
        ico._opts = self._opts.copy()
        return ico

    def _get_opts(self, state, mode: QIcon.Mode) -> IconOptions:
        opts = self._opts[state][mode] or self._default_opts
        if opts.color is None:
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

        # font
        font = QFont()
        font.setFamily(opts.font_family)
        font.setPixelSize(round(rect.height() * opts.scale_factor))
        if opts.font_style:
            font.setStyleName(opts.font_style)

        # color
        c_args = opts.color if isinstance(opts.color, tuple) else (opts.color,)

        # animation
        if opts.animation is not None:
            opts.animation.animate(painter, rect, mode)  # TODO

        painter.save()
        painter.setPen(QColor(*c_args))
        painter.setOpacity(opts.opacity)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, opts.glyph)
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
        glyph: str,
        font_family: str,
        state: QIcon.State = QIcon.State.On,
        mode: QIcon.Mode = QIcon.Mode.Normal,
        font_style: Optional[str] = None,
        scale_factor: float = DEFAULT_SCALING_FACTOR,
        color: Union[
            QColor,
            int,
            str,
            Qt.GlobalColor,
            Tuple[int, int, int, int],
            Tuple[int, int, int],
            None,
        ] = None,
        opacity: float = 1,
        animation: Optional[Animation] = None,
        transform: Optional[QTransform] = None,
    ):
        """Set icon options for a specific mode/state."""
        self._engine._opts[state][mode] = IconOptions(
            glyph,
            font_family,
            font_style,
            scale_factor,
            color,
            opacity,
            animation,
            transform,
        )


class QFontIconFactory(QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        self._registered_fonts: DefaultDict[str, Set[str]] = DefaultDict(set)
        self._registered_enums: Dict[Enum, Tuple[int, str, List[str]]] = dict()

    def addFont(self, font: StringOrEnum) -> bool:
        """Add font to registry."""
        if isinstance(font, (Path, str)):
            filename: Union[str, Path] = font
        else:
            font = ensure_font_enum_type(font)
            filename = font._font_file()

        assert Path(filename).exists(), f"Font file doesn't exist: {filename}"

        fontId = QFontDatabase.addApplicationFont(str(Path(filename).absolute()))
        if fontId < 0:
            warnings.warn(f"Cannot load font file: {filename}")
            return False

        families = QFontDatabase.applicationFontFamilies(fontId)
        if not families:
            warnings.warn(f"Font file is empty!: {filename}")
            return False
        font_family = families[0]

        if tuple(QT_VERSION.split(".")) < ("6", "0"):
            styles = QFontDatabase().styles(font_family)
        else:
            styles = QFontDatabase.styles(font_family)  # type: ignore
        if not styles:
            warnings.warn("Family with no styles is not supported")
            return False

        # if the font is already registered... remove the duplicate from the database.
        if self._registered_fonts[font_family].issuperset(styles):
            warnings.warn(
                f"Font {font_family!r} with styles {styles} is already registered."
            )
            QFontDatabase.removeApplicationFont(fontId)
            return False

        if is_font_enum_type(font):
            self._registered_enums[font] = (fontId, font_family, styles)
        self._registered_fonts[font_family].update(styles)
        return True

    def icon(
        self,
        key_or_enum: Union[str, Enum],
        **options: Any,  # TODO
    ) -> QFontIcon:
        family, style, glyph = self._get_family_and_glpyh(key_or_enum)
        default_opts = IconOptions(glyph, family, style, **(options or {}))
        return QFontIcon(default_opts)

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

    def _get_family_and_glpyh(self, key_or_enum):
        enum = str2enum(key_or_enum) if isinstance(key_or_enum, str) else key_or_enum
        if not is_font_enum_member(enum):
            raise TypeError(
                f"{key_or_enum} must be a string (icon key) or a FontEnum member"
            )
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

    def registeredFonts(self) -> Dict[str, Set[str]]:
        """Return registered font list (family and styles)."""
        return dict(self._registered_fonts)

    def isRegistered(self, font_family: StringOrEnum) -> bool:
        """Return `True` if `font_family` is registered."""
        return font_family in self

    def __contains__(self, font: StringOrEnum) -> bool:
        if isinstance(font, str):
            return any(font.lower() == key.lower() for key in self._registered_fonts)
        return ensure_font_enum_type(font) in self._registered_enums
