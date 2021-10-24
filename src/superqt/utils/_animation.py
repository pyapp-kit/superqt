"""Different animators to be used for animating components"""
# from math import sin, cos, radians

from ..qtcompat.QtCore import QEasingCurve, QPropertyAnimation, QVariantAnimation
from ..qtcompat.QtGui import QIcon, QPixmap, QTransform
from ..qtcompat.QtWidgets import QAbstractButton, QWidget


# =================================================================================================
def create_hide_show_animation(
    widget: QWidget = None,
    duration: int = 500,
    easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
) -> QPropertyAnimation:
    """
    Creates an animation that can be used to show animation while hiding and revealing the widget.
    """
    animation: QPropertyAnimation
    if widget is not None:
        animation = QPropertyAnimation(
            targetObject=widget, propertyName=b"maximumHeight"
        )
        animation.setEndValue(widget.sizeHint().height() + 10)
    else:
        animation = QPropertyAnimation()
        animation.setEndValue(0)

    # Create the animation
    animation.setStartValue(0)
    animation.setEasingCurve(easing_curve)
    animation.setDuration(duration)

    return animation


# =================================================================================================
def create_icon_rotation_animation(
    widget: QAbstractButton,
    duration: int = 500,
    easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
    start_value: float = 0.0,
    end_value: float = 90.0,
) -> QVariantAnimation:
    """
    Creates a rotation animation
    """
    animation = QVariantAnimation(
        widget, startValue=start_value, endValue=end_value, duration=duration
    )
    animation.setEasingCurve(easing_curve)
    pixmap = widget.icon.pixmap(widget.iconSize())
    original_length = pixmap.width()

    def on_value_changed(value):
        # Calculate new size
        # rad = radians(value)
        # new_length = (abs(sin(rad)) + abs(cos(rad)))*original_length

        transform = QTransform()
        transform.rotate(value)
        transformed_pixmap: QPixmap = pixmap.transformed(transform)
        xoffset = (transformed_pixmap.width() - original_length) / 2
        yoffset = (transformed_pixmap.height() - original_length) / 2
        transformed_pixmap = transformed_pixmap.copy(
            xoffset, yoffset, original_length, original_length
        )

        icon = QIcon(transformed_pixmap)
        widget.setIcon(icon)

    animation.updateCurrentValue = on_value_changed

    return animation


# =================================================================================================
