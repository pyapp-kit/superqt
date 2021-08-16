from superqt import QElidingLabel
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])

labl = QElidingLabel(
    "a skj skjfskfj sdlf sdfl sdlfk jsdf sdlkf jdsf dslfksdl sdlfk sdf sdl "
    "fjsdlf kjsdlfk laskdfsal as lsdfjdsl kfjdslf asfd dslkjfldskf sdlkfj"
)
labl.setWordWrap(True)
labl.show()
app.exec_()
