from superqt import QLabeledRangeSlider, QLabeledSlider


def test_labeled_slider_api(qtbot):
    slider = QLabeledRangeSlider()
    qtbot.addWidget(slider)
    slider.hideBar()
    slider.showBar()
    slider.setBarVisible()
    slider.setBarMovesAllHandles()
    slider.setBarIsRigid()


def test_slider_connect_works(qtbot):
    slider = QLabeledSlider()
    qtbot.addWidget(slider)

    slider._label.editingFinished.emit()
