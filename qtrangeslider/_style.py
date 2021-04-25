import platform
import re
from dataclasses import dataclass, replace
from typing import Union

from .qtcompat.QtCore import Qt
from .qtcompat.QtGui import (
    QColor,
    QGradient,
    QLinearGradient,
    QPalette,
    QRadialGradient,
)
from .qtcompat.QtWidgets import QApplication, QSlider


@dataclass
class RangeSliderStyle:
    brush_active: str = None
    brush_inactive: str = None
    brush_disabled: str = None
    pen_active: str = None
    pen_inactive: str = None
    pen_disabled: str = None
    vertical_thickness: float = None
    horizontal_thickness: float = None
    tick_offest: float = None

    def brush(self, cg: QPalette.ColorGroup) -> Union[QGradient, QColor]:
        attr = {
            QPalette.Active: "brush_active",  # 0
            QPalette.Disabled: "brush_disabled",  # 1
            QPalette.Inactive: "brush_inactive",  # 2
        }[cg]
        val = getattr(self, attr) or getattr(SYSTEM_STYLE, attr)
        if isinstance(val, str):
            val = QColor(val)
        return val

    def offset(self, tp: QSlider.TickPosition) -> int:
        val = self.tick_offest or SYSTEM_STYLE.tick_offest
        if tp & QSlider.TicksAbove:
            return val
        elif tp & QSlider.TicksBelow:
            return -val
        else:
            return 0

    def thickness(self, orientation: Qt.Orientation) -> float:
        if orientation == Qt.Horizontal:
            return self.horizontal_thickness or SYSTEM_STYLE.horizontal_thickness
        else:
            return self.vertical_thickness or SYSTEM_STYLE.vertical_thickness


# ##########  System-specific default styles ############

CATALINA_STYLE = RangeSliderStyle(
    brush_active="#3B88FD",
    brush_inactive="#8F8F8F",
    brush_disabled="#BBBBBB",
    horizontal_thickness=3,
    vertical_thickness=3,
    tick_offest=4,
)

BIG_SUR_STYLE = replace(CATALINA_STYLE)

SYSTEM = platform.system()
if SYSTEM == "Darwin":
    if int(platform.mac_ver()[0].split(".", maxsplit=1)[0]) >= 11:
        SYSTEM_STYLE = BIG_SUR_STYLE
    else:
        SYSTEM_STYLE = CATALINA_STYLE
elif SYSTEM == "Windows":
    SYSTEM_STYLE = RangeSliderStyle()
elif SYSTEM == "Linux":
    LINUX = True
    SYSTEM_STYLE = RangeSliderStyle()
else:
    SYSTEM_STYLE = RangeSliderStyle()


# ################ Stylesheet parsing logic ########################

qlineargrad_pattern = re.compile(
    r"""
    qlineargradient\(
        x1:\s*(?P<x1>\d*\.?\d+),\s*
        y1:\s*(?P<y1>\d*\.?\d+),\s*
        x2:\s*(?P<x2>\d*\.?\d+),\s*
        y2:\s*(?P<y2>\d*\.?\d+),\s*
        stop:0\s*(?P<stop0>\S+),.*
        stop:1\s*(?P<stop1>\S+)
    \)""",
    re.X,
)

qradial_pattern = re.compile(
    r"""
    qradialgradient\(
        cx:\s*(?P<cx>\d*\.?\d+),\s*
        cy:\s*(?P<cy>\d*\.?\d+),\s*
        radius:\s*(?P<radius>\d*\.?\d+),\s*
        fx:\s*(?P<fx>\d*\.?\d+),\s*
        fy:\s*(?P<fy>\d*\.?\d+),\s*
        stop:0\s*(?P<stop0>\S+),.*
        stop:1\s*(?P<stop1>\S+)
    \)""",
    re.X,
)


def parse_color(color: str) -> Union[str, QGradient]:
    qc = QColor(color)
    if qc.isValid():
        return qc

    # try linear gradient:
    match = qlineargrad_pattern.match(color)
    if match:
        grad = QLinearGradient(*[float(i) for i in match.groups()[:4]])
        grad.setColorAt(0, QColor(match.groupdict()["stop0"]))
        grad.setColorAt(1, QColor(match.groupdict()["stop1"]))
        return grad

    # try linear gradient:
    match = qradial_pattern.match(color)
    print("match", match.groupdict())
    if match:
        grad = QRadialGradient(*[float(i) for i in match.groups()[:5]])
        grad.setColorAt(0, QColor(match.groupdict()["stop0"]))
        grad.setColorAt(1, QColor(match.groupdict()["stop1"]))
        return grad

    # fallback to dark gray
    return "#333"


def update_styles_from_stylesheet(obj):
    qss = obj.styleSheet()
    p = obj
    while p.parent():
        qss = p.styleSheet() + qss
        p = p.parent()
    qss = QApplication.instance().styleSheet() + qss

    # Find bar color
    # TODO: optional horizontal or vertical
    match = re.search(r"Slider::sub-page:?([^{\s]*)?\s*{\s*([^}]+)}", qss, re.S)
    if match:
        orientation, content = match.groups()
        for line in reversed(content.splitlines()):
            bgrd = re.search(r"background(-color)?:\s*([^;]+)", line)
            if bgrd:
                obj._style.brush_active = parse_color(bgrd.groups()[-1])
                # TODO: bar color inactive?
                # TODO: bar color disabled?
                class_name = type(obj).__name__
                _ss = f"\n{class_name}::sub-page:{orientation}{{background: none}}"
                # TODO: block double event
                obj.setStyleSheet(qss + _ss)
                break

    # Find bar height/width
    for orient, dim in (("horizontal", "height"), ("vertical", "width")):
        match = re.search(rf"Slider::groove:{orient}\s*{{\s*([^}}]+)}}", qss, re.S)
        if match:
            for line in reversed(match.groups()[0].splitlines()):
                bgrd = re.search(rf"{dim}\s*:\s*(\d+)", line)
                if bgrd:
                    thickness = float(bgrd.groups()[-1])
                    setattr(obj._style, f"{orient}_thickness", thickness)
