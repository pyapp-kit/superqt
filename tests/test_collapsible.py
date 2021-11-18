"""A test module for testing collapsible"""

from superqt import QCollapsible
from superqt.qtcompat.QtCore import QEasingCurve
from superqt.qtcompat.QtWidgets import QPushButton


def test_checked_initialization(qtbot):
    """Test simple collapsible"""
    wdg1 = QCollapsible("Advanced analysis")
    wdg1.quickExpand()
    assert wdg1.expanded() is True
    assert wdg1._content.maximumHeight() > 0

    wdg2 = QCollapsible("Advanced analysis")
    wdg1.quickCollapse
    assert wdg2.expanded() is False
    assert wdg2._content.maximumHeight() == 0


def test_content_hide_show(qtbot):
    """Test collapsible with content"""

    # Create child component
    collapsible = QCollapsible("Advanced analysis")
    for i in range(10):
        collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

    collapsible.quickCollapse()
    assert collapsible.expanded() is False
    assert collapsible._content.maximumHeight() == 0

    collapsible.quickExpand()
    assert collapsible.expanded() is True
    assert collapsible._content.maximumHeight() > 0


def test_locking(qtbot):
    """Test locking collapsible"""
    wdg1 = QCollapsible()
    assert wdg1.locked() is False
    wdg1.setLocked(True)
    assert wdg1.locked() is True

    # Simulate button press
    wdg1._toggle_btn.setChecked(True)
    wdg1._toggle()

    assert wdg1.expanded() is False


def test_changing_animation_settings(qtbot):
    """Quick test for changing animation settings"""
    wdg = QCollapsible()
    wdg.setDuration(600)
    wdg.setEasingCurve(QEasingCurve.InElastic)
    assert wdg._animation.easingCurve() == QEasingCurve.InElastic
    assert wdg._animation.duration() == 600


def test_changing_content(qtbot):
    """Test changing the content"""
    content = QPushButton()
    wdg = QCollapsible()
    wdg.setContent(content)
    assert wdg._content == content
