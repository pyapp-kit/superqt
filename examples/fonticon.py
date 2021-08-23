from fonticon_fa5 import FA5S

from superqt.fonticon import icon, pulse, setTextIcon, spin
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

# btn = QPushButton()
# ic = icon("bs.alarm", color="blue")
# ic.addState(state=QIcon.Mode.Disabled, color='red')
# btn.setIcon(ic)
# btn.setIconSize(QSize(256, 256))
# btn.show()

btn = QPushButton()
btn.setIcon(
    icon(
        FA5S.ambulance,
        color="blue",
        states={
            "active": {
                "glyph": FA5S.bath,
                "color": "red",
                "scale_factor": 0.5,
                "animation": pulse(btn),
            },
            "disabled": {"color": "green", "scale_factor": 0.8, "animation": spin(btn)},
        },
    )
)
btn.setIconSize(QSize(256, 256))
btn.show()

# btn2 = QPushButton()
# btn2.setIcon(icon("fa5b.500px", animation=pulse(btn2)))
# btn2.setIconSize(QSize(225, 225))
# btn2.show()

btn3 = QPushButton()
btn3.resize(275, 275)
setTextIcon(btn3, FA5S.air_freshener)
btn3.show()


app.exec()
