from superqt import QSearchableComboBox


class TestSearchableComboBox:
    def test_constructor(self, qtbot):
        widget = QSearchableComboBox()
        qtbot.addWidget(widget)

    def test_add_items(self, qtbot):
        widget = QSearchableComboBox()
        qtbot.addWidget(widget)
        widget.addItems(["foo", "bar"])
        assert widget.completer_object.model().rowCount() == 2
        widget.addItem("foobar")
        assert widget.completer_object.model().rowCount() == 3
        widget.insertItem(1, "baz")
        assert widget.completer_object.model().rowCount() == 4
        widget.insertItems(2, ["bazbar", "foobaz"])
        assert widget.completer_object.model().rowCount() == 6
        assert widget.itemText(0) == "foo"
        assert widget.itemText(1) == "baz"
        assert widget.itemText(2) == "bazbar"

    def test_completion(self, qtbot):
        widget = QSearchableComboBox()
        qtbot.addWidget(widget)
        widget.addItems(["foo", "bar", "foobar", "baz", "bazbar", "foobaz"])

        widget.completer_object.setCompletionPrefix("fo")
        assert widget.completer_object.completionCount() == 3
        assert widget.completer_object.currentCompletion() == "foo"
        widget.completer_object.setCurrentRow(1)
        assert widget.completer_object.currentCompletion() == "foobar"
        widget.completer_object.setCurrentRow(2)
        assert widget.completer_object.currentCompletion() == "foobaz"
