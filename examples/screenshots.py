import pathlib
from itertools import product

from pyqrangeslider import QRangeSlider
from pyqrangeslider.qtcompat.QtCore import Qt
from pyqrangeslider.qtcompat.QtWidgets import QApplication

dest = pathlib.Path("screenshots")
dest.mkdir(exist_ok=True)

app = QApplication([])

orientations = ("horizontal", "vertical")
ticks = ("NoTicks", "TicksAbove", "TicksBelow")

variants = [
    # (min, max), orient, ticks,
    ((20, 80), "horizontal"),
    ((20, 80), "vertical"),
]

for orient, tick in product(orientations, ticks):
    slider = QRangeSlider(getattr(Qt, orient.title()))
    slider.setRange(0, 100)
    slider.setValue((20, 80))
    slider.setTickPosition(getattr(slider, tick))
    slider.activateWindow()
    if orient == "horizontal":
        slider.setFixedWidth(300)
    else:
        slider.setFixedHeight(200)
    app.processEvents()
    fname = dest / f"grab_{orient[:1]}_{tick}.png"
    slider.grab().save(str(fname))
    slider.close()
