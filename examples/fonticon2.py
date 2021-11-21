try:
    from fonticon_fa5 import FA5S
except ImportError as e:
    raise type(e)(
        "This example requires the fontawesome fontpack:\n\n"
        "pip install git+https://github.com/tlambert03/fonticon-fontawesome5.git"
    )

from qtpy.QtWidgets import QApplication, QPushButton

from superqt.fonticon import setTextIcon

app = QApplication([])


btn4 = QPushButton()
btn4.resize(275, 275)
setTextIcon(btn4, FA5S.hamburger)
btn4.show()

app.exec()
