"""A collapsible widget to hide and unhide child widgets"""
from typing import Union

from ..qtcompat.QtCore import QAbstractAnimation, QEasingCurve, QParallelAnimationGroup
from ..qtcompat.QtGui import QIcon
from ..qtcompat.QtWidgets import QLayout, QPushButton, QStyle, QWidget
from ..utils._animators import create_hide_show_animator

# =================================================================================================


class QCollapsible(QPushButton):
    """
    A collapsible widget to hide and unhide child widgets. This is based on simonxeko solution
    https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
    """

    title: str
    animator: QParallelAnimationGroup
    lock_to: bool
    content: Union[QWidget, QLayout]
    icon: QIcon

    def __init__(
        self,
        content: Union[QWidget, QLayout] = None,
        duration: int = 500,
        initial_is_checked: bool = False,
        lock_to: bool = None,
        easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
        is_transparent: bool = True,
        text_alignment: str = "left",
        **kwargs,
    ):
        """Initializes the component"""

        # Call parent initialization
        super().__init__(**kwargs)

        # Initialize variables
        self.title = self.text()
        self.lock_to = lock_to
        self.content = content

        # Modify style
        self.setCheckable(True)

        # Apply special styles
        style_string = ""
        if is_transparent:
            style_string = style_string + "background:rgba(255, 255, 255, 0); "
        style_string = style_string + f"text-align: {text_alignment};"
        self.setStyleSheet(style_string)

        # Add icon
        # icons_directory = pathlib.Path(__file__).parent / "resources"
        # icon_filename = icons_directory / "triangle-fill-svgrepo-com.svg"
        # icon_filename = icons_directory / "right-arrow-black-triangle.png"

        # icon = QIcon(str(icon_filename))
        # self.setIconSize(QtCore.QSize(24,24))

        # Set icon
        pixmapi = getattr(QStyle, "SP_MediaPlay")
        self.icon = self.style().standardIcon(pixmapi)
        self.setIcon(self.icon)

        # Create animators
        self.animator = create_hide_show_animator(
            content, duration=duration, easing_curve=easing_curve
        )

        # Set conent and button initial state
        self.setChecked(initial_is_checked)
        if content is not None:
            if initial_is_checked is False:
                content.setMaximumHeight(0)
            else:
                pass
        # self.refresh_icon()

        # Connect events
        self.clicked.connect(self.toggle_hidden)

    # ===========================================
    def set_animator_settings(
        self,
        duration: int = 500,
        easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
    ):
        """Update the animator settings"""
        self.animator.setEasingCurve(easing_curve)
        self.animator.setDuration(duration)

    # ===========================================
    def set_content(self, content: Union[QWidget, QLayout] = None):
        """Sets the content to collapse"""
        if isinstance(content, QLayout):
            self.content = QWidget()
            self.content.setLayout(content)
        else:
            self.content = content

        self.animator.setTargetObject(content)
        self.animator.setPropertyName(b"maximumHeight")
        self.animator.setEndValue(content.sizeHint().height() + 10)

    # ===========================================
    def toggle_hidden(self) -> None:
        """Toggle the hidden state of the frame"""

        if self.lock_to is not None and self.isChecked() != self.lock_to:
            self.setChecked(self.lock_to)
            self.refresh_icon()
            return

        if self.lock_to is not None:
            self.setChecked(self.lock_to)

        if self.content is not None:
            self.show_content() if self.isChecked() else self.hide_content()

        self.refresh_icon()

    # ===========================================
    def refresh_icon(self):
        """Updates the icon of the button based on the status"""
        if self.isChecked():
            self.setText("▼ " + self.title)
        else:
            self.setText("▲ " + self.title)

    # ===========================================
    def hide_content(self):
        """Hides the content"""
        if self.content is not None:
            self.animator.setDirection(QAbstractAnimation.Direction.Backward)
            self.animator.start()

    # ===========================================
    def show_content(self):
        """Show the content"""
        if self.content is not None:
            self.animator.setDirection(QAbstractAnimation.Direction.Forward)
            self.animator.start()


# =================================================================================================
