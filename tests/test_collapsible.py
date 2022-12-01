"""A test module for testing collapsible"""

from qtpy.QtCore import QEasingCurve, Qt
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QPushButton, QStyle, QWidget

from superqt import QCollapsible


def _get_builtin_icon(name: str) -> QIcon:
    """Get a built-in icon from the Qt library."""
    widget = QWidget()
    try:
        pixmap = getattr(QStyle.StandardPixmap, f"SP_{name}")
    except AttributeError:
        pixmap = getattr(QStyle, f"SP_{name}")

    return widget.style().standardIcon(pixmap)


def test_checked_initialization(qtbot):
    """Test simple collapsible"""
    wdg1 = QCollapsible("Advanced analysis")
    wdg1.expand(False)
    assert wdg1.isExpanded()
    assert wdg1._content.maximumHeight() > 0

    wdg2 = QCollapsible("Advanced analysis")
    wdg1.collapse(False)
    assert not wdg2.isExpanded()
    assert wdg2._content.maximumHeight() == 0


def test_content_hide_show(qtbot):
    """Test collapsible with content"""

    # Create child component
    collapsible = QCollapsible("Advanced analysis")
    for i in range(10):
        collapsible.addWidget(QPushButton(f"Content button {i + 1}"))

    collapsible.collapse(False)
    assert not collapsible.isExpanded()
    assert collapsible._content.maximumHeight() == 0

    collapsible.expand(False)
    assert collapsible.isExpanded()
    assert collapsible._content.maximumHeight() > 0


def test_locking(qtbot):
    """Test locking collapsible"""
    wdg1 = QCollapsible()
    assert wdg1.locked() is False
    wdg1.setLocked(True)
    assert wdg1.locked() is True
    assert not wdg1.isExpanded()

    wdg1._toggle_btn.setChecked(True)
    assert not wdg1.isExpanded()

    wdg1._toggle()
    assert not wdg1.isExpanded()

    wdg1.expand()
    assert not wdg1.isExpanded()

    wdg1._toggle_btn.setChecked(False)
    assert not wdg1.isExpanded()

    wdg1.setLocked(False)
    wdg1.expand()
    assert wdg1.isExpanded()
    assert wdg1._toggle_btn.isChecked()


def test_changing_animation_settings(qtbot):
    """Quick test for changing animation settings"""
    wdg = QCollapsible()
    wdg.setDuration(600)
    wdg.setEasingCurve(QEasingCurve.Type.InElastic)
    assert wdg._animation.easingCurve() == QEasingCurve.Type.InElastic
    assert wdg._animation.duration() == 600


def test_changing_content(qtbot):
    """Test changing the content"""
    content = QPushButton()
    wdg = QCollapsible()
    wdg.setContent(content)
    assert wdg._content == content


def test_changing_text(qtbot):
    """Test changing the content"""
    wdg = QCollapsible()
    wdg.setText("Hi new text")
    assert wdg.text() == "Hi new text"
    assert wdg._toggle_btn.text() == "Hi new text"


def test_toggle_signal(qtbot):
    """Test that signal is emitted when widget expanded/collapsed."""
    wdg = QCollapsible()
    with qtbot.waitSignal(wdg.toggled, timeout=500):
        qtbot.mouseClick(wdg._toggle_btn, Qt.LeftButton)

    with qtbot.waitSignal(wdg.toggled, timeout=500):
        wdg.expand()

    with qtbot.waitSignal(wdg.toggled, timeout=500):
        wdg.collapse()


def test_getting_icon(qtbot):
    """Test setting string as toggle button."""
    wdg = QCollapsible("test")
    assert isinstance(wdg.expandedIcon(), QIcon)
    assert isinstance(wdg.collapsedIcon(), QIcon)


def test_setting_icon(qtbot):
    """Test setting icon for toggle button."""
    icon1 = _get_builtin_icon("ArrowRight")
    icon2 = _get_builtin_icon("ArrowDown")
    wdg = QCollapsible("test", expandedIcon=icon1, collapsedIcon=icon2)
    assert wdg._expanded_icon == icon1
    assert wdg._collapsed_icon == icon2


def test_setting_symbol_icon(qtbot):
    """Test setting string as toggle button."""
    wdg = QCollapsible("test")
    icon1 = wdg._convert_string_to_icon("+")
    icon2 = wdg._convert_string_to_icon("-")
    wdg.setCollapsedIcon(icon=icon1)
    assert wdg._collapsed_icon == icon1
    wdg.setExpandedIcon(icon=icon2)
    assert wdg._expanded_icon == icon2
