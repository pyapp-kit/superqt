from unittest.mock import Mock

from superqt.utils import qdebounced, qthrottled


def test_debounced(qtbot):
    mock1 = Mock()
    mock2 = Mock()

    @qdebounced(timeout=5)
    def f1() -> str:
        mock1()

    def f2() -> str:
        mock2()

    for _ in range(10):
        f1()
        f2()

    qtbot.wait(5)
    mock1.assert_called_once()
    assert mock2.call_count == 10


def test_throttled(qtbot):
    mock1 = Mock()
    mock2 = Mock()

    @qthrottled(timeout=5)
    def f1() -> str:
        mock1()

    def f2() -> str:
        mock2()

    for _ in range(10):
        f1()
        f2()

    qtbot.wait(5)
    assert mock1.call_count == 2
    assert mock2.call_count == 10
