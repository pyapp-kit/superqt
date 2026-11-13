"""Renderer for the docs' widget screenshots and animations.

Run it with `docs/_gen_media.py`; animations and capture options live in
`docs/_scenes.py`.

Widgets are drawn with one of two styles (`--style`):

- `fusion` (default): Qt's Fusion style, with palettes that match the site,
  rendered offscreen. Works anywhere, needs no display, and runs in parallel.
- `macos`: Qt's native macOS style, with the system's light and dark appearance.
  Only on macOS, and with real windows: Qt's offscreen platform can't draw this
  style, and windows that aren't shown are drawn as inactive. So the windows
  appear on screen while they're rendered, one at a time.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

SCALE = 2  # device pixel ratio of the rendered images
STYLES = ("fusion", "macos")
STYLE = os.environ.get("SUPERQT_DOCS_STYLE", "fusion")  # (set by `main` for workers)
_ENVIRON = dict(os.environ)  # (for the workers, before it's changed here)
if STYLE == "fusion":
    os.environ["QT_QPA_PLATFORM"] = "offscreen"  # deterministic, and headless
    os.environ["QT_SCALE_FACTOR"] = str(SCALE)

from PIL import Image  # noqa: E402
from qtpy import API_NAME, QT_VERSION, QtWidgets  # noqa: E402
from qtpy.QtCore import (  # noqa: E402
    QPoint,
    QPointF,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    qInstallMessageHandler,
)
from qtpy.QtGui import (  # noqa: E402
    QColor,
    QFont,
    QFontDatabase,
    QGuiApplication,
    QImage,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPixmap,
)
from qtpy.QtTest import QTest  # noqa: E402
from qtpy.QtWidgets import QApplication, QWidget  # noqa: E402

from superqt.sliders import _range_style  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

DOCS = Path(__file__).parent
EXAMPLES = DOCS / "examples"
OUT = DOCS / "_generated"
MANIFEST = OUT / "manifest.json"
MARGIN = 14  # logical px of window background around each capture
FPS = 30
FONTS = ("Inter", "Inter Variable", "Helvetica Neue", "Segoe UI", "Noto Sans")

# Fusion palettes, tuned to sit on the light and dark zensical "modern" theme
# (the macOS style uses the system's colors instead).
# Keep `Highlight` in sync with `--sq-accent` in docs/stylesheets/extra.css.
THEMES: dict[str, dict[str, str]] = {
    "light": {
        "Window": "#f3f4f7",
        "Button": "#fbfbfc",
        "Base": "#ffffff",
        "AlternateBase": "#eef0f4",
        "Text": "#1d2129",
        "WindowText": "#1d2129",
        "ButtonText": "#1d2129",
        "PlaceholderText": "#868c97",
        "Highlight": "#4d5bd8",
        "HighlightedText": "#ffffff",
        "ToolTipBase": "#ffffff",
        "ToolTipText": "#1d2129",
        "Link": "#4d5bd8",
    },
    "dark": {
        "Window": "#1b1e25",
        "Button": "#272b34",
        "Base": "#13151a",
        "AlternateBase": "#1f232a",
        "Text": "#e3e6ec",
        "WindowText": "#e3e6ec",
        "ButtonText": "#e3e6ec",
        "PlaceholderText": "#7c8390",
        "Highlight": "#6f7cf2",
        "HighlightedText": "#ffffff",
        "ToolTipBase": "#272b34",
        "ToolTipText": "#e3e6ec",
        "Link": "#8f9aff",
    },
}

PAD = 10  # logical px of window background around an outlined main window
# (backdrop, window outline): behind windows that don't fill the image
BACKDROPS = {"light": ("#e3e6eb", "#c5cad3"), "dark": ("#0f1115", "#3a3f4b")}


# ---------------------------------------------------------------------------
# Specs: how each example is captured (registered in docs/_scenes.py)


@dataclass
class Spec:
    """How to capture one example."""

    width: int | None = None  # resize the window to this width (logical px)
    height: int | None = None  # ... and/or this height
    # for continuous motion: no pause at the start or end, and frames at exact
    # intervals, so that the last frame leads straight back into the first
    seamless: bool = False
    setup: Callable[[QWidget], Any] | None = None  # called before capturing
    scene: Callable[[Recorder, QWidget], Any] | None = None  # records an animation

    def source(self) -> str:
        funcs = [f for f in (self.setup, self.scene) if f is not None]
        sizes = (self.width, self.height, self.seamless)
        return repr(sizes) + "".join(map(inspect.getsource, funcs))


SPECS: dict[str, Spec] = {}


def spec(name: str, **kwargs: Any) -> Spec:
    """Register capture options for `docs/examples/<name>.py`."""
    SPECS[name] = Spec(**kwargs)
    return SPECS[name]


def scene(name: str, **kwargs: Any) -> Callable:
    """Decorator: register `func(recorder, window)` as the animation for `name`."""

    def _deco(func: Callable) -> Callable:
        spec(name, scene=func, **kwargs)
        return func

    return _deco


# ---------------------------------------------------------------------------
# Capturing


@dataclass
class Frame:
    """The visible windows (global geometry, image) and cursor at one instant."""

    windows: list[tuple[QRect, QImage]]
    cursor: QPointF | None = None
    pressed: bool = False
    t: float = 0.0


def _capture(main: QWidget, cursor: QPointF | None = None, pressed=False) -> Frame:
    # the main window first, then popups etc. on top of it
    tops = [main] + [
        w for w in QApplication.topLevelWidgets() if w is not main and w.isVisible()
    ]
    windows = [
        (QRect(w.mapToGlobal(QPoint(0, 0)), w.size()), _grab(w))
        for w in tops
        if w.isVisible()
    ]
    return Frame(windows, cursor, pressed, time.perf_counter())


def _grab(widget: QWidget) -> QImage:
    """Render a window at `SCALE`, whatever the pixel ratio of its screen."""
    pixmap = QPixmap(widget.size() * SCALE)
    pixmap.setDevicePixelRatio(SCALE)
    pixmap.fill(Qt.GlobalColor.transparent)
    widget.render(pixmap)
    return pixmap.toImage()


def _window_color() -> QColor:
    return QApplication.palette().window().color()


def _compose(frames: list[Frame], theme: str) -> list[QImage]:
    """Paint frames onto canvases with a common size (the union of all windows).

    If the main window always fills the canvas, it's drawn as is, on a margin of
    its own background. Otherwise (popups, resizing) windows are outlined on a
    backdrop, so that you can see where they end.
    """
    windows = [frame.windows[0][0] for frame in frames]
    flat = all(len(f.windows) == 1 and f.windows[0][0] == windows[0] for f in frames)
    pad = 0 if flat else PAD
    bounds = QRect()
    for frame in frames:
        for i, (rect, _) in enumerate(frame.windows):
            bounds = bounds.united(
                rect.adjusted(-pad, -pad, pad, pad) if i == 0 else rect
            )
    bounds.adjust(-MARGIN, -MARGIN, MARGIN, MARGIN)

    window_color = _window_color()
    backdrop, outline = (QColor(c) for c in BACKDROPS[theme])
    images = []
    for frame in frames:
        img = QImage(bounds.size() * SCALE, QImage.Format.Format_ARGB32_Premultiplied)
        img.setDevicePixelRatio(SCALE)
        img.fill(window_color if flat else backdrop)
        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, (rect, win_img) in enumerate(frame.windows):
            rect = rect.translated(-bounds.topLeft())
            if not flat:
                panel = rect.adjusted(-pad, -pad, pad, pad) if i == 0 else rect
                painter.fillRect(panel.translated(0, 2), QColor(0, 0, 0, 28))  # shadow
                painter.fillRect(panel, window_color)
                painter.setPen(QPen(outline, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(QRectF(panel).adjusted(-0.5, -0.5, 0.5, 0.5))
            painter.drawImage(rect.topLeft(), win_img)
        if frame.cursor is not None:
            _draw_cursor(painter, frame.cursor - QPointF(bounds.topLeft()), frame)
        painter.end()
        images.append(img)
    return images


_ARROW = [(0, 0), (0, 15.5), (4, 12), (6.6, 18), (9, 17), (6.5, 11), (11.5, 11)]


def _draw_cursor(painter: QPainter, pos: QPointF, frame: Frame) -> None:
    if frame.pressed:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(120, 130, 255, 90))
        painter.drawEllipse(pos, 11, 11)
    path = QPainterPath()
    path.moveTo(pos + QPointF(*_ARROW[0]))
    for x, y in _ARROW[1:]:
        path.lineTo(pos + QPointF(x, y))
    path.closeSubpath()
    painter.setPen(QPen(QColor("white"), 1.3))
    painter.setBrush(QColor(20, 20, 20))
    painter.drawPath(path)


class Recorder:
    """Drives a window with synthetic input, recording frames in real time.

    Positions are in the coordinates of the widget they're given with (its center
    by default), and the cursor is drawn into the frames.
    """

    def __init__(self, window: QWidget, fps: int = FPS) -> None:
        self.window = window
        self.frames: list[Frame] = []
        self.inactive_frames = 0
        self.moved = False
        self._origin = QPoint()
        self._interval = 1 / fps
        self._next = time.perf_counter()
        self._cursor: QPointF | None = None
        self._pressed = False
        self._grab: QWidget | None = None  # (the window that the button was pressed on)

    # -- primitives --

    def frame(self) -> None:
        """Process events until the next frame is due, then capture it."""
        # (if we fell behind, capture now: frame durations come from timestamps)
        self._next = max(self._next + self._interval, time.perf_counter())
        while (remaining := self._next - time.perf_counter()) > 0:
            QTest.qWait(max(1, int(remaining * 1000)))
        if not _ensure_active(self.window):
            self.inactive_frames += 1
        frame = _capture(self.window, self._cursor, self._pressed)
        if self.frames and frame.windows[0][0].topLeft() != self._origin:
            self.moved = True  # (by something else: real input, with the macos style)
        self._origin = frame.windows[0][0].topLeft()
        self.frames.append(frame)

    def wait(self, seconds: float) -> None:
        for _ in range(max(1, round(seconds / self._interval))):
            self.frame()

    def _global(self, widget: QWidget | None, pos: QPoint | QPointF | None) -> QPointF:
        widget = widget or self.window
        if pos is None:
            pos = widget.rect().center()
        return QPointF(widget.mapToGlobal(QPointF(pos)))

    def _window_at_cursor(self) -> QWidget | None:
        """The window under the cursor: an open popup or modal dialog, or the window."""
        assert self._cursor is not None
        pos = self._cursor.toPoint()
        modal = QApplication.activeModalWidget()
        windows = [QApplication.activePopupWidget(), modal, self.window]
        for window in filter(None, windows):
            if QRect(window.mapToGlobal(QPoint(0, 0)), window.size()).contains(pos):
                return window
        return None

    def _send(self, kind: str) -> None:
        """Send a mouse event to the window under the cursor (in its coordinates).

        While the button is pressed, events go to the window that it was pressed on.
        """
        assert self._cursor is not None
        under = self._window_at_cursor()
        if kind == "press":
            self._grab = under or self.window
        target = self._grab if self._pressed or kind == "release" else under
        if target is None:  # (a move outside of the windows)
            return
        origin = QPointF(target.mapToGlobal(QPoint(0, 0)))
        local = (self._cursor - origin).toPoint()
        win = target.windowHandle()
        btn, mod = Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
        if kind == "move":
            QTest.mouseMove(win, local)
        elif kind == "press":
            QTest.mousePress(win, btn, mod, local)
        else:
            QTest.mouseRelease(win, btn, mod, local)

    # -- gestures --

    def move(
        self,
        widget: QWidget | None = None,
        pos: QPoint | QPointF | None = None,
        duration: float = 0.5,
    ) -> None:
        """Glide the cursor to `pos` in `widget` (dragging, if pressed)."""
        end = self._global(widget, pos)
        if self._cursor is None:  # the cursor enters from below
            self._cursor = end + QPointF(40, 60)
        start = QPointF(self._cursor)
        steps = max(1, round(duration / self._interval))
        for i in range(1, steps + 1):
            t = _ease(i / steps)
            self._cursor = start + (end - start) * t
            self._send("move")
            self.frame()

    def press(self) -> None:
        self._pressed = True
        self._send("press")
        self.wait(0.12)

    def release(self, wait: float = 0.12) -> None:
        self._pressed = False
        self._send("release")
        if wait:
            self.wait(wait)

    def click(self, widget: QWidget | None = None, pos=None, **kwargs: Any) -> None:
        self.move(widget, pos, **kwargs)
        self.press()
        self.release()

    def drag(self, widget: QWidget | None, start, end, duration: float = 0.8) -> None:
        self.move(widget, start)
        self.press()
        self.move(widget, end, duration)
        self.release()

    def click_into_modal(
        self,
        widget: QWidget,
        pos: QPoint | QPointF | None,
        then: Callable[[QWidget], Any],
    ) -> None:
        """Click something that opens a modal dialog, and record `then(dialog)`.

        A modal dialog runs its own event loop (`exec()`) inside the click, so `then`
        runs (and records) inside that loop. It should close the dialog.
        """

        def _in_dialog() -> None:
            if (dialog := QApplication.activeModalWidget()) is None:
                QTimer.singleShot(10, _in_dialog)  # (not open yet)
                return
            QTest.qWaitForWindowExposed(dialog)
            then(dialog)

        self.move(widget, pos)
        self.press()
        QTimer.singleShot(0, _in_dialog)
        self.release()

    def type(self, widget: QWidget, text: str, interval: float = 0.09) -> None:
        widget.setFocus()
        for char in text:
            QTest.keyClick(widget, char)
            self.wait(interval)

    def key(self, widget: QWidget, key: Qt.Key, times: int = 1, interval=0.1) -> None:
        for _ in range(times):
            QTest.keyClick(widget, key)
            self.wait(interval)

    def leave(self, duration: float = 0.4) -> None:
        """Move the cursor off the bottom of the window, and hide it."""
        bottom = self.window.rect().bottomRight() + QPoint(30, 40)
        self.move(None, bottom, duration)
        self._cursor = None

    def resize(
        self,
        width: int | None = None,
        height: int | None = None,
        duration: float = 1.0,
        fit_height: bool = False,
    ) -> None:
        """Animate the window size (with `fit_height`, height follows the width)."""
        start = self.window.size()
        end = QSize(width or start.width(), height or start.height())
        steps = max(1, round(duration / self._interval))
        for i in range(1, steps + 1):
            t = _ease(i / steps)
            w = round(start.width() + (end.width() - start.width()) * t)
            h = round(start.height() + (end.height() - start.height()) * t)
            if fit_height:
                h = self.window.heightForWidth(w)
            self.window.resize(w, h)
            self.frame()


def _ease(t: float) -> float:
    return 4 * t**3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


# ---------------------------------------------------------------------------
# Running examples


class _AppProxy:
    """Stands in for the `QApplication` that an example creates."""

    def __init__(self, app: QApplication) -> None:
        self._app = app

    def exec(self, *_: Any) -> int:
        return 0

    exec_ = exec

    def __getattr__(self, name: str) -> Any:
        return getattr(self._app, name)


class _AppShimMeta(type):
    def __call__(cls, *_: Any, **__: Any) -> _AppProxy:
        return _AppProxy(QApplication.instance())

    def __getattr__(cls, name: str) -> Any:
        return getattr(QApplication, name)


class _AppShim(metaclass=_AppShimMeta):
    pass


@contextmanager
def _patched_qapplication() -> Iterator[None]:
    """Make `QApplication([])` return the running app, and `exec()` return at once."""
    QtWidgets.QApplication = _AppShim  # type: ignore[misc]
    try:
        yield
    finally:
        QtWidgets.QApplication = QApplication  # type: ignore[misc]


def _run_example(name: str) -> tuple[QWidget, dict]:
    """Run an example, returning the window it shows (and its namespace)."""
    path = EXAMPLES / f"{name}.py"
    code = compile(path.read_text(), str(path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(path)}
    with _patched_qapplication():
        try:
            exec(code, namespace)
        except SystemExit:
            pass
    shown = [w for w in QApplication.topLevelWidgets() if w.isVisible()]
    if len(shown) != 1:
        raise RuntimeError(f"{path.name} should show one window, not {len(shown)}")
    QTest.qWaitForWindowExposed(shown[0])
    return shown[0], namespace


def _ensure_active(window: QWidget, timeout: int = 1000) -> bool:
    """With the macos style, make `window` active (inactive windows are gray)."""
    if STYLE != "macos" or window.isActiveWindow():
        return True
    if QApplication.activePopupWidget() or QApplication.activeModalWidget():
        return True  # (a popup, or a dialog, of the window has the focus)
    window.raise_()
    window.activateWindow()
    return QTest.qWaitForWindowActive(window, timeout)


def _clear_focus() -> None:
    if widget := QApplication.focusWidget():
        widget.clearFocus()


# ---------------------------------------------------------------------------
# Workers


_QUIET = ("propagateSizeHints", "Populating font family aliases")


def _qt_message_handler(mode: Any, context: Any, message: str) -> None:
    if not message.startswith(_QUIET) and "propagateSizeHints" not in message:
        print(message, file=sys.stderr)


def _make_app() -> QApplication:
    qInstallMessageHandler(_qt_message_handler)
    app = QApplication([])
    if STYLE == "macos":
        app.setStyle("macos")  # (with the system font)
        return app
    app.setStyle("Fusion")
    families = set(QFontDatabase.families())
    if family := next((f for f in FONTS if f in families), None):
        app.setFont(QFont(family, 10))
    return app


def _set_theme(theme: str) -> None:
    hints = QGuiApplication.styleHints()
    if hasattr(hints, "setColorScheme"):  # Qt >= 6.8
        scheme = Qt.ColorScheme.Dark if theme == "dark" else Qt.ColorScheme.Light
        hints.setColorScheme(scheme)
    elif STYLE == "macos":
        raise RuntimeError("the macos style needs Qt >= 6.8, to switch themes")
    if STYLE == "macos":
        return  # (the style uses the system's colors for the scheme)

    colors = THEMES[theme]
    palette = QPalette(QColor(colors["Button"]), QColor(colors["Window"]))
    for role, color in colors.items():
        palette.setColor(getattr(QPalette.ColorRole, role), QColor(color))
    disabled = QColor(colors["PlaceholderText"])
    for role in ("Text", "WindowText", "ButtonText"):
        role_ = getattr(QPalette.ColorRole, role)
        palette.setColor(QPalette.ColorGroup.Disabled, role_, disabled)
    QApplication.setPalette(palette)

    # QRangeSlider's bar color is hard-coded per OS; use the theme's accent instead,
    # so the docs look the same wherever they're built
    accent = QColor(colors["Highlight"])
    _range_style.SYSTEM_STYLE = replace(
        _range_style.LINUX_STYLE,
        brush_active=accent.name(),
        brush_inactive=accent.name(),
        brush_disabled=colors["PlaceholderText"],
        pen_active=accent.darker(125).name(),
        pen_inactive=accent.darker(125).name(),
        pen_disabled=colors["PlaceholderText"],
    )


def _to_pil(img: QImage) -> Image.Image:
    img = img.convertToFormat(QImage.Format.Format_RGBA8888)
    ptr = img.constBits()
    if hasattr(ptr, "setsize"):  # PyQt
        ptr.setsize(img.sizeInBytes())
    size = (img.width(), img.height())
    return Image.frombuffer("RGBA", size, bytes(ptr), "raw", "RGBA", 0, 1)


def _save_animation(
    frames: list[Frame], images: list[QImage], dest: Path, seamless: bool = False
) -> None:
    pils: list[Image.Image] = []
    durations: list[int] = []
    if seamless:
        times = [i / FPS for i in range(len(frames) + 1)]
    else:
        times = [f.t for f in frames] + [frames[-1].t + 1 / FPS]
    for i, img in enumerate(images):
        pil = _to_pil(img).convert("RGB")
        ms = round(times[i + 1] * 1000) - round(times[i] * 1000)  # (no drift)
        if pils and pil.tobytes() == pils[-1].tobytes():
            durations[-1] += ms  # merge repeated frames
        else:
            pils.append(pil)
            durations.append(ms)
    if not seamless:
        durations[-1] += 1200  # rest on the last frame before looping
    pils[0].save(
        dest,
        save_all=True,
        append_images=pils[1:],
        duration=durations,
        loop=0,
        lossless=True,
        method=4,
    )


def _resize(window: QWidget, width: int | None, height: int | None) -> None:
    """Resize to `width` and/or `height` (if only width: the height that fits)."""
    if not (width or height):
        return
    width = width or window.width()
    height = height or window.heightForWidth(width)
    if height <= 0:
        height = window.sizeHint().height()
    window.resize(width, height)


def _render(name: str, theme: str) -> dict[str, Any]:
    """Render one example in one theme (in a fresh process: see `_work`)."""
    _set_theme(theme)
    spec = SPECS.get(name, Spec())
    window, _namespace = _run_example(name)  # (keeps the example's objects alive)
    if spec.width or spec.height:
        _resize(window, spec.width, spec.height)
    if spec.setup is not None:
        spec.setup(window)
    _clear_focus()  # no text cursor or focus ring in stills
    QTest.qWait(50)
    if not _ensure_active(window, 3000):
        print(f"warning: {name}'s window wasn't active", file=sys.stderr)

    still = _compose([_capture(window)], theme)[0]
    _to_pil(still).save(OUT / f"{name}-{theme}.png", optimize=True)
    info: dict[str, Any] = {
        "width": still.width() // SCALE,
        "height": still.height() // SCALE,
        "background": _window_color().name(),
    }
    if spec.scene is not None:
        rec = Recorder(window)
        if not spec.seamless:
            rec.wait(0.5)
        spec.scene(rec, window)
        if not spec.seamless:
            rec.wait(0.6)
        if rec.moved:
            print(f"warning: {name}'s window moved while recording", file=sys.stderr)
        if rec.inactive_frames:
            n = rec.inactive_frames
            print(
                f"warning: {name}'s window was inactive in {n} frames", file=sys.stderr
            )
        images = _compose(rec.frames, theme)
        _save_animation(rec.frames, images, OUT / f"{name}-{theme}.webp", spec.seamless)
        info["animation"] = {
            "width": images[0].width() // SCALE,
            "height": images[0].height() // SCALE,
        }
    return info


# ---------------------------------------------------------------------------
# Main


def _work(name: str, theme: str) -> None:
    """Render in a worker process, print the result, and exit without Qt teardown."""
    import _scenes  # noqa: F401  (registers specs)

    app = _make_app()  # noqa: F841
    print(_RESULT + json.dumps(_render(name, theme)), flush=True)
    os._exit(0)


_RESULT = "@@result "


def _run_job(name: str, theme: str, style: str) -> tuple[dict | None, str]:
    cmd = [sys.executable, str(DOCS / "_gen_media.py"), "--worker", name, theme]
    env = {**_ENVIRON, "SUPERQT_DOCS_STYLE": style}
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
    for line in proc.stdout.splitlines():
        if line.startswith(_RESULT):
            return json.loads(line[len(_RESULT) :]), proc.stderr
    return None, proc.stderr or f"exited with {proc.returncode}"


def _hash(name: str, style: str) -> str:
    src = [
        (EXAMPLES / f"{name}.py").read_text(),
        Path(__file__).read_text(),
        SPECS.get(name, Spec()).source(),
        f"{API_NAME} {QT_VERSION} {style}",
    ]
    return hashlib.sha256("\0".join(src).encode()).hexdigest()[:16]


def _outputs_exist(name: str, info: dict) -> bool:
    exts = ["png"] + (["webp"] if "animation" in info else [])
    return all((OUT / f"{name}-{t}.{e}").exists() for t in THEMES for e in exts)


def main(argv: list[str] | None = None, description: str = "") -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("names", nargs="*", help="examples to render (default: all)")
    parser.add_argument("-f", "--force", action="store_true", help="ignore the cache")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count())
    parser.add_argument(
        "-s",
        "--style",
        choices=STYLES,
        default="fusion",
        help="Qt style to draw the widgets with (default: fusion; see _media.py)",
    )
    parser.add_argument("--worker", nargs=2, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker:
        _work(*args.worker)
    if args.style == "macos":
        if sys.platform != "darwin":
            parser.error("the macos style is only available on macOS")
        args.jobs = 1  # (only one window can be active at a time)
        print(
            "Rendering with the macos style: windows will appear on screen.\n"
            "Don't move the mouse over them, or type, until it's done."
        )

    import _scenes  # noqa: F401  (registers specs)

    available = sorted(p.stem for p in EXAMPLES.glob("*.py"))
    if unknown := set(args.names) - set(available):
        parser.error(f"no such example(s): {', '.join(sorted(unknown))}")
    OUT.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    manifest = {k: v for k, v in manifest.items() if k in available}

    todo = [
        name
        for name in args.names or available
        if args.force
        or manifest.get(name, {}).get("hash") != _hash(name, args.style)
        or not _outputs_exist(name, manifest[name])
    ]
    print(f"rendering {len(todo)} of {len(args.names or available)} examples")

    t0 = time.perf_counter()
    failed: set[str] = set()
    results: dict[str, dict[str, dict]] = {}
    jobs = [(name, theme) for name in todo for theme in THEMES]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_run_job, *job, args.style): job for job in jobs}
        for future in as_completed(futures):
            (name, theme), (info, stderr) = futures[future], future.result()
            if info is None:
                failed.add(name)
                print(f"  ✗ {name} ({theme})\n{stderr}", file=sys.stderr)
                continue
            print(f"  ✓ {name} ({theme})")
            for line in stderr.splitlines():
                if line.startswith("warning:"):
                    print(f"    {line}")
            results.setdefault(name, {})[theme] = info

    for name, infos in results.items():
        if name in failed:
            manifest.pop(name, None)
            continue
        # sizes are the same in both themes; the window color isn't
        backgrounds = {theme: info.pop("background") for theme, info in infos.items()}
        manifest[name] = {
            "hash": _hash(name, args.style),
            "style": args.style,
            **infos["light"],
            "background": backgrounds,
        }
    for name in failed:
        manifest.pop(name, None)
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=2) + "\n")
    print(f"done in {time.perf_counter() - t0:.1f}s")
    return 1 if failed else 0
