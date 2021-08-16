from superqt import QElidingLabel
from superqt.qtcompat.QtWidgets import QApplication

app = QApplication([])

labl = QElidingLabel(
    "a skj skjfskfj sdlf sdfl sdlfk jsdf sdlkf jdsf dslfksdlfk sdlfk sdf sdl fjsdlf kjsdlfk jsldkfjsdlkfj sdlkfj"
)
labl.setWordWrap(True)
labl.show()
app.exec_()
