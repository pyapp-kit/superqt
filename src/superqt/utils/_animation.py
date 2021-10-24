"""Different animators to be used for animating components"""
from ..qtcompat.QtGui import QIcon, QTransform
from ..qtcompat.QtCore import QEasingCurve, QPropertyAnimation, QVariantAnimation, Slot, Signal
from ..qtcompat.QtWidgets import QWidget


# =================================================================================================
def create_hide_show_animation(
    widget: QWidget = None,
    duration: int = 500,
    easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic,
) -> QPropertyAnimation:
    """
    Creates an animation that can be used to show animation while hiding and revealing the widget.
    """
    animation:QPropertyAnimation
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
def create_rotation_animation(
    widget: QWidget, 
    duration:int = 500, 
    easing_curve: QEasingCurve = QEasingCurve.Type.InOutCubic
) -> QVariantAnimation:
    """
    Creates a rotation animation
    """
    
    @Signal()
    def on_valueChanged(self, value):
        t = QTransform()
        t.rotate(value)
        widget.setPixmap(widget.pixmap.transformed(t))
        
    animation = QVariantAnimation(startValue=0.0, endValue=360.0, duration=1000, on_valueChanged=on_valueChanged)

    return animation
# =================================================================================================


#     def set_pixmap(self, pixmap):
#         self._pixmap = pixmap
#         self.setPixmap(self._pixmap)

#     @QtCore.pyqtSlot(QtCore.QVariant)
#     def on_valueChanged(self, value):
#         t = QtGui.QTransform()
#         t.rotate(value)
#         self.setPixmap(self._pixmap.transformed(t))
