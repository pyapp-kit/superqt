import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    DefaultDict,
    Dict,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
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

from ._font_enum import FontEnum, is_font_enum_type


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


StringOrFontEnum = Union[str, Type[FontEnum]]


class QFontIcon(QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self._registered_fonts: DefaultDict[str, Set[str]] = defaultdict(set)

    def addFont(self, font: StringOrFontEnum) -> bool:
        """Add font to registry."""
        if isinstance(font, (Path, str)):
            filename: Union[str, Path] = font
        elif hasattr(font, "_font_file"):
            filename = font._font_file()
        else:
            raise TypeError(
                "'font' must be either a Path, string, or an Enum object with a method "
                f"'_font_file' that returns a file path to a font file. got: {type(font)}"
            )
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
        print("added", font_family, styles)
        self._registered_fonts[font_family].update(styles)
        return True

    @overload
    def icon(self, family_or_enum: FontEnum, **options: Any) -> QIcon:
        """Return icon."""
        ...

    @overload
    def icon(
        self,
        family_or_enum: str,
        style: str,
        glyph: str,
        **options: Any,
    ) -> QIcon:
        """Return icon."""
        ...

    def icon(
        self,
        family_or_enum: Union[str, FontEnum],
        style: str = "",
        glyph: str = "",
        **options: Any,
    ) -> QIcon:
        if is_font_enum_type(type(family_or_enum)):
            if family_or_enum not in self:
                self.addFont(family_or_enum)
            family_or_enum = cast(FontEnum, family_or_enum)
            style = family_or_enum._font_style()
            glyph = family_or_enum.value
            _family = family_or_enum._font_family()
        elif isinstance(family_or_enum, str):
            _family = family_or_enum
            assert glyph
            assert style

        icon_opts = IconOptions(_family, style, glyph, **(options or {}))
        return QIcon(QFontIconEngine(icon_opts))

    def font(self, family, style: str = None, size: int = None) -> QFont:
        if is_font_enum_type(type(family)) or is_font_enum_type(family):
            if family not in self:
                self.addFont(family)
            style = family._font_style()
            _family = family._font_family()
        else:
            _family = family

        font = QFont()
        font.setFamily(_family)
        if style:
            font.setStyleName(style)
        if size:
            font.setPixelSize(size)
        return font

    def registeredFonts(self) -> Dict[str, Set[str]]:
        """Return registered font list (family and styles)."""
        return dict(self._registered_fonts)

    def isRegistered(self, font_family: str) -> bool:
        """Return `True` if `font_family` is registered."""
        return font_family in self

    def __contains__(self, font: StringOrFontEnum) -> bool:
        if isinstance(font, str):
            font_family = font
        elif hasattr(font, "_font_family"):
            font_family = font._font_family()
        else:
            raise TypeError(
                "'font' must be either a string, or an Enum object with a method "
                "'font_family_' that returns a file path to a font file."
            )

        return any(font_family.lower() == key.lower() for key in self._registered_fonts)
