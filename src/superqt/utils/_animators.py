"""Different animators to be used for animating components"""
from ..qtcompat.QtCore import QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from ..qtcompat.QtWidgets import QWidget


# =================================================================================================
def create_hide_show_animator(
    widget: QWidget = None,
    duration: int = 500,
    easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
) -> QParallelAnimationGroup:
    """
    Creates an animator that can be used to show animation while hiding and revealing the widget.
    """

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

    # Creates the animator
    animator = QParallelAnimationGroup()
    animator.addAnimation(animation)

    return animator


# =================================================================================================
def create_rotation_animator(widget: QWidget) -> QParallelAnimationGroup:

    # if widget is not None:
    #     animation = QPropertyAnimation(targetObject=widget,  propertyName=b"maximumHeight")
    #     animation.setEndValue(widget.sizeHint().height()+10)
    # else:
    #     animation = QPropertyAnimation()
    #     animation.setEndValue(0)
    pass
