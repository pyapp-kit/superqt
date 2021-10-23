import sys

from superqt import QCollapsible
from superqt.qtcompat.QtCore import Qt
from superqt.qtcompat.QtWidgets import (
    QApplication,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

app = QApplication([])

main_widget = QWidget()
main_widget.setMinimumWidth(500)
main_widget.setMinimumHeight(700)

layout = QVBoxLayout()
layout.setAlignment(Qt.AlignTop)

icons = [
    "SP_ArrowRight",
    "SP_MediaPlay",
]
for n, name in enumerate(icons):
    btn = QPushButton(name)

    pixmapi = getattr(QStyle, name)
    icon = main_widget.style().standardIcon(pixmapi)
    btn.setIcon(icon)
    layout.addWidget(btn)


# Create child component
inner_layout = QVBoxLayout()
inner_widget = QWidget()
for i in range(10):
    conetent_button = QPushButton(text="Content button " + str(i + 1))
    inner_layout.addWidget(conetent_button)
inner_widget.setLayout(inner_layout)

# Create collapsible
collapsible = QCollapsible(
    text="Advanced analysis",
    content=inner_widget,
    duration=2000,
    initial_is_checked=True,
)

layout.addWidget(collapsible)
layout.addWidget(inner_widget)

# Show
main_widget.setLayout(layout)
main_widget.show()
sys.exit(app.exec_())
