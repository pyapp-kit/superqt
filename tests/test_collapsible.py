"""A test module for testing collapsible"""

from superqt import QCollapsible
from superqt.qtcompat.QtCore import QEasingCurve
from superqt.qtcompat.QtWidgets import QPushButton, QVBoxLayout, QWidget


# =================================================================================================
def test_checked_initialization(qtbot):
    """Test simple collapsible"""
    wdg1 = QCollapsible(initial_is_checked=True)
    assert wdg1.isChecked() is True

    wdg2 = QCollapsible(initial_is_checked=False)
    assert wdg2.isChecked() is False


# =================================================================================================
def test_content_hide_show(qtbot):
    """Test collapsible with content"""

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
        duration=0,
        initial_is_checked=True,
    )

    collapsible._hideContent()
    assert collapsible.content.maximumHeight() == 0
    collapsible._showContent()
    assert collapsible.content.maximumHeight() >= 600

    collapsible.setChecked(False)
    collapsible._toggleHidden()
    assert collapsible.isChecked() is False
    assert collapsible.content.maximumHeight() == 0

    collapsible.setChecked(True)
    collapsible._toggleHidden()
    assert collapsible.isChecked() is True
    assert collapsible.content.maximumHeight() > 600


# =================================================================================================
def test_locking(qtbot):
    """Test locking collapsible"""
    wdg1 = QCollapsible(initial_is_checked=True, lock_to=False)
    assert wdg1.isChecked() is False

    wdg2 = QCollapsible(initial_is_checked=False, lock_to=False)
    assert wdg2.isChecked() is False


# =================================================================================================
def test_changing_animation_settings(qtbot):
    """Quick test for changing animation settings"""
    wdg = QCollapsible(duration=300)
    wdg.setAnimatorsSettings(duration=600, easing_curve=QEasingCurve.InElastic)
    assert wdg.hide_show_animation.easingCurve() == QEasingCurve.InElastic
    assert wdg.hide_show_animation.duration() == 600
    assert wdg.rotate_animation.easingCurve() == QEasingCurve.InElastic
    assert wdg.rotate_animation.duration() == 600


# =================================================================================================
def test_changing_content(qtbot):

    content = QPushButton()
    wdg = QCollapsible()
    assert wdg.content is None
    wdg.setContent(content)
    assert wdg.content is not None


# =================================================================================================
