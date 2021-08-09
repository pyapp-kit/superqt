import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, EnumMeta
from inspect import ismethod
from pathlib import Path
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    overload,
)

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
)
from superqt.qtcompat.QtWidgets import QApplication


def is_font_enum_type(obj) -> bool:
    """Return True if `obj` is a font enum capable of creating icons."""
    return (
        hasattr(obj, "_font_file")
        and ismethod(obj._font_file)
        and isinstance(obj, EnumMeta)
    )


def is_font_enum_member(obj) -> bool:
    """Return True if `obj` is a font enum member of creating icons."""
    return (
        hasattr(obj, "_font_file")
        and ismethod(obj._font_file)
        and isinstance(obj, Enum)
    )


def ensure_font_enum_type(obj) -> Enum:
    if is_font_enum_member(obj):
        return type(obj)
    if not is_font_enum_type(obj):
        raise TypeError(
            "must be either a string, or an Enum object with a "
            "'_font_file' method that returns a file path to a font file. "
            f"got: {type(obj)}"
        )
    return obj


def find_glyphname(enumclass: EnumMeta, glyphname: str) -> Enum:
    """Given a font enum class, find a glyph name that may be canonicalized"""
    import keyword

    member = getattr(enumclass, glyphname, None)
    if member is not None:
        return member

    _glyph = glyphname
    if glyphname[0].isdigit():
        glyphname = "_" + glyphname

    if keyword.iskeyword(glyphname):
        glyphname += "_"

    glyphname = glyphname.replace("-", "_")

    member = getattr(enumclass, glyphname, None)
    if member is not None:
        return member

    raise ValueError(f"FontEnum {enumclass} has no member: {_glyph} or {glyphname}")


@dataclass
class IconOptions:
    fontFamily: str
    fontStyle: str
    glyph: str
    fontFamilyOn: str = ""
    fontStyleOn: str = ""
    glyphOn: str = ""
    color: QColor = field(
        default_factory=lambda: QApplication.palette().color(
            QPalette.Normal, QPalette.ButtonText
        )
    )
    colorOn: QColor = QColor()
    colorActive: QColor = QColor()
    colorActiveOn: QColor = QColor()
    colorDisabled: QColor = field(
        default_factory=lambda: QApplication.palette().color(
            QPalette.Disabled, QPalette.ButtonText
        )
    )
    colorSelected: QColor = field(
        default_factory=lambda: QApplication.palette().color(
            QPalette.Active, QPalette.ButtonText
        )
    )
    scaleFactor: float = 0.85
    scaleFactorOn: float = 0


class QFontIconEngine(QIconEngine):
    def __init__(self, options: IconOptions):
        super().__init__()
        self._opt = options

    def clone(self) -> QIconEngine:
        return QFontIconEngine(self._opt)

    def _parse_options(
        self, rect: QRect, mode: QIcon.Mode, state: QIcon.State
    ) -> Tuple[QFont, QColor, str]:
        _fIcon = self._opt
        if state == QIcon.State.On:
            fontFamily = _fIcon.fontFamilyOn or _fIcon.fontFamily
            fontStyle = _fIcon.fontStyleOn or _fIcon.fontStyle
            glyph = _fIcon.glyphOn or _fIcon.glyph
            scalefactor = _fIcon.scaleFactorOn or _fIcon.scaleFactor
        else:
            fontFamily = _fIcon.fontFamily
            fontStyle = _fIcon.fontStyle
            glyph = _fIcon.glyph
            scalefactor = _fIcon.scaleFactor

        penColor = _fIcon.color
        colorOn = QColor(_fIcon.colorOn)
        colorActive = QColor(_fIcon.colorActive)
        colorActiveOn = QColor(_fIcon.colorActiveOn)
        if mode == QIcon.Mode.Normal:
            if state == QIcon.State.On and colorOn.isValid():
                penColor = colorOn
        elif mode == QIcon.Mode.Active:
            if state == QIcon.State.Off and colorActive.isValid():
                penColor = colorActive
            elif state == QIcon.State.On:
                if colorActiveOn.isValid():
                    penColor = colorActiveOn
                elif colorOn.isValid():
                    penColor = colorOn
        elif mode == QIcon.Mode.Disabled:
            penColor = _fIcon.colorDisabled
        elif mode == QIcon.Mode.Selected:
            penColor = _fIcon.colorSelected

        font = QFont()
        font.setFamily(fontFamily)
        if fontStyle:
            font.setStyleName(fontStyle)
        font.setPixelSize(int(round(rect.height() * scalefactor)))
        return font, penColor, glyph

    def paint(
        self,
        painter: QPainter,
        rect: QRect,
        mode: QIcon.Mode,
        state: QIcon.State,
    ) -> None:
        font, penColor, glyph = self._parse_options(rect, mode, state)
        painter.save()
        painter.setPen(penColor)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, glyph)
        painter.restore()

    def pixmap(self, size: QSize, mode: QIcon.Mode, state: QIcon.State) -> QPixmap:
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, QRect(QPoint(0, 0), size), mode, state)
        return pixmap


StringOrEnum = Union[str, Type[Enum]]


class QFontIcon(QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self._registered_fonts: DefaultDict[str, Set[str]] = defaultdict(set)
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

    @overload
    def icon(self, key_or_enum: Enum, **options: Any) -> QIcon:
        """Return icon."""
        ...

    @overload
    def icon(
        self,
        key_or_enum: str,
        style: str,
        glyph: str,
        **options: Any,
    ) -> QIcon:
        """Return icon."""
        ...

    def _parse_key(self, key: str):
        from . import _FONT_KEYS, discover_fonts

        key, glyph = key.split(".")
        if key not in _FONT_KEYS:
            discover_fonts()
        try:
            fontenum = _FONT_KEYS[key]
        except KeyError:
            raise ValueError(
                f"Unrecognized font key: {key}. Registered keys: {list(_FONT_KEYS)}"
            )
        if fontenum not in self._registered_enums:
            self.addFont(fontenum)

        glyph = find_glyphname(fontenum, glyph).value
        _, _family, styles = self._registered_enums[fontenum]
        return _family, styles[0], glyph

    def icon(
        self,
        key_or_enum: Union[str, Enum],
        style: str = "",
        glyph: str = "",
        **options: Any,
    ) -> QIcon:
        if isinstance(key_or_enum, str):
            _family, style, glyph = self._parse_key(key_or_enum)
        else:
            if not is_font_enum_member(key_or_enum):
                raise TypeError(
                    "The first argument to `icon` must be an icon key or "
                    "a FontEnum member"
                )
            glyph = key_or_enum.value
            fontenum = type(key_or_enum)

            if fontenum not in self._registered_enums:
                self.addFont(fontenum)
            _, _family, styles = self._registered_enums[fontenum]
            style = styles[0]

        icon_opts = IconOptions(_family, style, glyph, **(options or {}))
        return QIcon(QFontIconEngine(icon_opts))

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
