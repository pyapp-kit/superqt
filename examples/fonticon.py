from fonticon_fa5 import FA5S
from fonticon_mdi6 import MDI6

from superqt.fonticon import icon, pulse
from superqt.qtcompat.QtCore import QSize
from superqt.qtcompat.QtWidgets import QApplication, QPushButton

app = QApplication([])

# btn = QPushButton()
# ic = icon("bs.alarm", color="blue")
# ic.addState(state=QIcon.Mode.Disabled, color='red')
# btn.setIcon(ic)
# btn.setIconSize(QSize(256, 256))
# btn.show()

# btn = QPushButton()
# btn.setIcon(
#     icon(
#         FA5S.ambulance,
#         color="blue",
#         states={
#             "active": {
#                 "glyph": FA5S.bath,
#                 "color": "red",
#                 "scale_factor": 0.5,
#                 "animation": pulse(btn),
#             },
#             "disabled": {"color": "green", "scale_factor": 0.8, "animation": spin(btn)},
#         },
#     )
# )
# btn.setIconSize(QSize(256, 256))
# btn.show()

btn2 = QPushButton()
btn2.setIcon(icon(MDI6.abacus, animation=pulse(btn2)))
btn2.setIconSize(QSize(225, 225))
btn2.show()

btn3 = QPushButton()
btn3.setIcon(icon(FA5S.spinner, animation=pulse(btn3)))
btn3.setIconSize(QSize(225, 225))
btn3.show()

# btn3 = QPushButton()
# btn3.resize(275, 275)
# setTextIcon(btn3, FA5S.spinner)
# btn3.show()


app.exec()
