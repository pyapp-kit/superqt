from superqt import QLabeledDoubleSlider

if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication([])
    slider = QLabeledDoubleSlider()
    slider.editingFinished.connect(lambda: print("editingFinished"))
    slider.show()
    app.exec_()
