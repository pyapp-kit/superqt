try:
    from fonticon_fa5 import FA5S
except ImportError as e:
    raise type(e)(
        "This example requires the fontawesome fontpack:\n\n"
        "pip install git+https://github.com/tlambert03/fonticon-fontawesome5.git"
    )

from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt.fonticon import IconOpts, icon, pulse, spin

app = QApplication([])

btn = QPushButton()
btn.setIcon(
    icon(
        FA5S.smile,
        color="blue",
        states={
            "active": IconOpts(
                glyph_key=FA5S.spinner,
                color="red",
                scale_factor=0.5,
                animation=pulse(btn),
            ),
            "disabled": {"color": "green", "scale_factor": 0.8, "animation": spin(btn)},
        },
    )
)
btn.setIconSize(QSize(256, 256))
btn.show()


@btn.clicked.connect
def toggle_state():
    btn.setChecked(not btn.isChecked())


app.exec()
