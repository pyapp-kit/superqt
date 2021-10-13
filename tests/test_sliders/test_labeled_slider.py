from superqt import QLabeledRangeSlider


def test_labeled_slider_api(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.hideBar()
    slider.showBar()
    slider.setBarVisible()
    slider.setBarMovesAllHandles()
    slider.setBarIsRigid()
