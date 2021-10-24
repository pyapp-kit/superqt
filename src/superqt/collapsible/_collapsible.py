"""A collapsible widget to hide and unhide child widgets"""
import pathlib
from typing import Union

from PySide2.QtCore import QPropertyAnimation, QVariantAnimation
from PySide2.QtGui import QTransform

from ..qtcompat import QtCore
from ..qtcompat.QtCore import QAbstractAnimation, QEasingCurve, QParallelAnimationGroup
from ..qtcompat.QtGui import QIcon, QPixmap
from ..qtcompat.QtWidgets import QLayout, QPushButton, QWidget
from ..utils._animation import (
    create_hide_show_animation,
    create_icon_rotation_animation,
)

# =================================================================================================


class QCollapsible(QPushButton):
    """
    A collapsible widget to hide and unhide child widgets. This is based on simonxeko solution
    https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
    """

    title: str
    animator: QParallelAnimationGroup
    hide_show_animation: QPropertyAnimation
    rotate_animation: QVariantAnimation
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
        icons_directory = pathlib.Path(__file__).parent / "resources"
        icon_filename = str(icons_directory / "right-arrow-black-triangle-sharp.png")
        icon_pixmap = QPixmap()
        icon_pixmap.load(icon_filename)
        self.icon = QIcon(icon_pixmap)
        self.setIconSize(QtCore.QSize(20, 20))
        self.setIcon(self.icon)

        # Set conent and button initial state
        self.setChecked(initial_is_checked)
        if content is not None:
            if initial_is_checked is False:
                content.setMaximumHeight(0)
            else:
                transform = QTransform()
                transform.rotate(90)
                icon = QIcon(icon_pixmap.transformed(transform))
                self.setIcon(icon)
        # self.refresh_icon()

        # Create animators
        self.animator = QParallelAnimationGroup()
        self.hide_show_animation = create_hide_show_animation(
            content, duration=duration, easing_curve=easing_curve
        )
        self.rotate_animation = create_icon_rotation_animation(self, duration=duration)
        self.animator.addAnimation(self.hide_show_animation)
        self.animator.addAnimation(self.rotate_animation)

        # Connect events
        self.clicked.connect(self.toggle_hidden)

    # ===========================================
    def set_hide_show_animator_settings(
        self,
        duration: int = 500,
        easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
    ):
        """Update the animator settings"""
        self.hide_show_animation.setEasingCurve(easing_curve)
        self.hide_show_animation.setDuration(duration)

    # ===========================================
    def set_content(self, content: Union[QWidget, QLayout] = None):
        """Sets the content to collapse"""
        if isinstance(content, QLayout):
            self.content = QWidget()
            self.content.setLayout(content)
        else:
            self.content = content

        self.hide_show_animation.setTargetObject(content)
        self.hide_show_animation.setPropertyName(b"maximumHeight")
        self.hide_show_animation.setEndValue(content.sizeHint().height() + 10)

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
        # if self.isChecked():
        #     self.setArrowType(Qt.DownArrow)
        # else:
        #     self.setArrowType(Qt.RightArrow)

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
