from napari._qt import get_app, run
from napari._qt.qt_resources import QColoredSVGIcon
from qtpy.QtCore import QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QListWidget, QListWidgetItem

from superqt import fonticon

icons = {
    "2D": "fa5r.square",
    "3D": "fa5s.cube",
    "add": "fa5s.plus-circle",
    "check": "fa5s.check",
    "chevron_down": "fa5s.chevron-down",
    "chevron_left": "fa5s.chevron-left",
    "chevron_up": "fa5s.chevron-up",
    "circle": "fa5s.circle",
    "console": "fa5s.terminal",
    "copy_to_clipboard": "mdi6.clipboard-multiple-outline",
    "delete_shape": "fa5s.times",
    "delete": "fa5r.trash-alt",
    "direct": "fa5s.location-arrow",
    "down_arrow": "fa5s.caret-down",
    "drop_down": "",
    "ellipse": "mdi6.vector-circle",
    "erase": "fa5s.eraser",
    "fill": "fa5s.fill-drip",
    "grid": "fa5s.th",
    "help": "fa5s.question-circle",
    "home": "fa5s.home",
    "info": "fa5s.info-circle",
    "left_arrow": "fa5s.caret-left",
    "line": "mdi6.vector-line",
    "logo_silhouette": "",
    "long_left_arrow": "fa5s.long-arrow-alt-left",
    "long_right_arrow": "fa5s.long-arrow-alt-right",
    "minus": "fa5s.minus",
    "move_back": "mdi6.arrange-send-backward",
    "move_front": "mdi6.arrange-bring-to-front",
    "new_image": "fa5s.image",
    "new_labels": "fa5s.tag",
    "new_points": "",
    "new_shapes": "fa5s.shapes",
    "new_surface": "mdi6.star",
    "new_tracks": "",
    "new_vectors": "",
    "paint": "fa5s.paint-brush",
    "path": "mdi6.vector-polyline",
    "picker": "fa5s.eye-dropper",
    "plus": "fa5s.plus",
    "polygon": "fa5s.draw-polygon",
    "pop_out": "fa5r.clone",
    "rectangle": "mdi6.vector-square",
    "right_arrow": "fa5s.caret-right",
    "roll": "",
    "select": "fa5s.location-arrow",
    "shuffle": "fa5s.random",
    "square": "fa5s.square-full",
    "step_left": "fa5s.step-backward",
    "step_right": "fa5s.step-forward",
    "transpose": "",
    "up_arrow": "fa5s.caret-up",
    "vertex_insert": "",
    "vertex_remove": "",
    "visibility_off": "mdi6.eye-off-outline",
    "visibility": "mdi6.eye-outline",
    "warning": "fa5s.exclamation-triangle",
    "zoom": "fa5s.search",
}


class ButtonGrid(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setMovement(QListWidget.Static)  # The items cannot be moved by the user.
        self.setViewMode(QListWidget.IconMode)  # make items icons
        self.setResizeMode(QListWidget.Adjust)  # relayout when view is resized.
        self.setUniformItemSizes(True)  # better performance
        self.setIconSize(QSize(36, 36))
        self.setWordWrap(True)

    def addItem(self, napari=None, fontkey=None):
        if napari:
            icn = QColoredSVGIcon.from_resources(napari)
        elif fontkey:
            icn = fonticon.icon(fontkey)
        else:
            icn = QIcon()
        item = QListWidgetItem(icn, napari or fontkey or "   ")
        item.setSizeHint(QSize(60, 100))
        super().addItem(item)


app = get_app()

grid = ButtonGrid()

for name, fontkey in icons.items():
    grid.addItem(napari=name)
    grid.addItem(fontkey=fontkey)
    grid.addItem()

grid.show()
run()
