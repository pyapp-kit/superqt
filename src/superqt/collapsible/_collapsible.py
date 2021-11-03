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
        if lock_to is not None:
            self.setChecked(lock_to)
        else:
            self.setChecked(initial_is_checked)

        if content is not None:
            if initial_is_checked is False:
                content.setMaximumHeight(0)
            else:
                transform = QTransform()
                transform.rotate(90)
                icon = QIcon(icon_pixmap.transformed(transform))
                self.setIcon(icon)

        # Create animators
        self.animator = QParallelAnimationGroup()
        self.hide_show_animation = create_hide_show_animation(
            content, duration=duration, easing_curve=easing_curve
        )
        self.hide_show_animation.setTargetObject(content)
        self.rotate_animation = create_icon_rotation_animation(
            self, duration=duration, easing_curve=easing_curve
        )
        self.animator.addAnimation(self.hide_show_animation)
        self.animator.addAnimation(self.rotate_animation)

        # Connect events
        self.clicked.connect(self._toggleHidden)

    # ===========================================
    def setAnimatationsSettings(
        self,
        duration: int = 500,
        easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
    ):
        """Update the animator settings"""

        # Easing curve
        self.hide_show_animation.setEasingCurve(easing_curve)
        self.rotate_animation.setEasingCurve(easing_curve)

        # Duration
        self.hide_show_animation.setDuration(duration)
        self.rotate_animation.setDuration(duration)

    # ===========================================
    def setContent(self, content: Union[QWidget, QLayout] = None):
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
    def _toggleHidden(self) -> None:
        """Toggle the hidden state of the frame"""

        if self.lock_to is not None and self.isChecked() != self.lock_to:
            self.setChecked(self.lock_to)
            return

        if self.lock_to is not None:
            self.setChecked(self.lock_to)

        if self.content is not None:
            self._showContent() if self.isChecked() else self._hideContent()

    # ===========================================
    def _hideContent(self):
        """Hides the content"""
        if self.content is not None:
            self.animator.setDirection(QAbstractAnimation.Direction.Backward)
            self.animator.start()

    # ===========================================
    def _showContent(self):
        """Show the content"""
        if self.content is not None:
            self.animator.setDirection(QAbstractAnimation.Direction.Forward)
            self.animator.start()


# =================================================================================================
