from superqt import QSearchableListWidget


class TestSearchableListWidget:
    def test_create(self, qtbot):
        widget = QSearchableListWidget()
        qtbot.addWidget(widget)
        widget.addItem("aaa")
        assert widget.count() == 1

    def test_add_items(self, qtbot):
        widget = QSearchableListWidget()
        qtbot.addWidget(widget)
        widget.addItems(["foo", "bar"])
        assert widget.count() == 2
        widget.insertItems(1, ["baz", "foobaz"])
        widget.insertItem(2, "foobar")
        assert widget.count() == 5
        assert widget.item(0).text() == "foo"
        assert widget.item(1).text() == "baz"
        assert widget.item(2).text() == "foobar"

    def test_completion(self, qtbot):
        widget = QSearchableListWidget()
        qtbot.addWidget(widget)
        widget.show()
        widget.addItems(["foo", "bar", "foobar", "baz", "bazbar", "foobaz"])
        widget.filter_widget.setText("fo")
        assert widget.count() == 6
        for i in range(widget.count()):
            item = widget.item(i)
            assert item.isHidden() == ("fo" not in item.text())

        widget.hide()
