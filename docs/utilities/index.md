# Utilities

Functions, classes, and decorators for working with Qt, in `superqt.utils`,
`superqt.fonticon`, and `superqt.cmap`.

## Icons

superqt has two ways to create icons from icon libraries: see
[Icons](icons/index.md) for how they compare.

| Object | Description |
| --- | --- |
| [`QIconifyIcon`](icons/iconify.md) | A `QIcon` with any of the SVG icons from [Iconify](https://iconify.design/). |
| [`icon`](icons/fonticon.md#superqt.fonticon.icon) | Create a `QIcon` from a glyph in an icon font. |
| [`setTextIcon`](icons/fonticon.md#superqt.fonticon.setTextIcon) | Show a glyph from an icon font as the text of a widget. |
| [`font`](icons/fonticon.md#superqt.fonticon.font) | Create the `QFont` of an icon font. |
| [`addFont`](icons/fonticon.md#superqt.fonticon.addFont) | Add an OTF or TTF font file to the icon font registry. |
| [`IconFont`](icons/fonticon.md#superqt.fonticon.IconFont) | Base class for defining the glyphs of an icon font. |
| [`IconFontMeta`](icons/fonticon.md#superqt.fonticon.IconFontMeta) | Metaclass of `IconFont`, which turns its attributes into glyph keys. |
| [`ENTRY_POINT`](icons/fonticon.md#superqt.fonticon.ENTRY_POINT) | The entry point group that font plugins register with. |
| [`IconOpts`](icons/fonticon.md#superqt.fonticon.IconOpts) | Options for drawing an icon in a given state (color, scale, and so on). |
| [`Animation`](icons/fonticon.md#superqt.fonticon.Animation), [`spin`](icons/fonticon.md#superqt.fonticon.spin), [`pulse`](icons/fonticon.md#superqt.fonticon.pulse) | Animations for font icons. |

## Threading

| Object | Description |
| --- | --- |
| [`thread_worker`](threading.md#superqt.utils.thread_worker) | Decorator that makes a function, or generator, run in another thread when called. |
| [`create_worker`](threading.md#superqt.utils.create_worker) | Create a worker that runs a function, or generator, in another thread. |
| [`FunctionWorker`](threading.md#superqt.utils.FunctionWorker) | `QRunnable` with signals, that runs a function. |
| [`GeneratorWorker`](threading.md#superqt.utils.GeneratorWorker) | `QRunnable` with signals, that runs a generator (and can be paused, resumed, and sent values). |
| [`WorkerBase`](threading.md#superqt.utils.WorkerBase) | Base class of the workers. |
| [`new_worker_qthread`](threading.md#superqt.utils.new_worker_qthread) | Run a `QObject` worker in a new `QThread`. |
| [`ensure_main_thread`](thread_decorators.md#superqt.utils.ensure_main_thread) | Decorator that makes a function run in the main thread. |
| [`ensure_object_thread`](thread_decorators.md#superqt.utils.ensure_object_thread) | Decorator that makes a `QObject` method run in the object's thread. |

## Signals

| Object | Description |
| --- | --- |
| [`qthrottled`](throttling.md#superqt.utils.qthrottled) | Decorator that limits how often a function runs. |
| [`qdebounced`](throttling.md#superqt.utils.qdebounced) | Decorator that delays a function until it stops being called. |
| [`QSignalThrottler`](throttling.md#superqt.utils.QSignalThrottler) | Emits its `triggered` signal at most once per timeout, however often `throttle()` is called. |
| [`QSignalDebouncer`](throttling.md#superqt.utils.QSignalDebouncer) | Emits its `triggered` signal once `throttle()` hasn't been called for a timeout. |
| [`signals_blocked`](signal_utils.md#superqt.utils.signals_blocked) | Context manager that blocks the signals of `QObject`s. |

## Messages and errors

| Object | Description |
| --- | --- |
| [`QMessageHandler`](qmessagehandler.md) | Context manager that captures Qt's log messages (from `qDebug`, `qWarning`, and so on). |
| [`exceptions_as_dialog`](error_dialog_contexts.md) | Context manager that shows exceptions in a dialog. |

## Miscellaneous

| Object | Description |
| --- | --- |
| [`CodeSyntaxHighlight`](code_syntax_highlight.md) | A `QSyntaxHighlighter` that highlights code with Pygments. |
| [`draw_colormap`](cmap.md#superqt.cmap.draw_colormap) | Draw a colormap onto a `QPainter` or `QPaintDevice`. |
| [`QColormapItemDelegate`](cmap.md#superqt.cmap.QColormapItemDelegate) | An item delegate that draws colormaps in item views. |
| [`qimage_to_array`](images.md) | Convert a `QImage` to a NumPy array. |
| [`QStyleOptionToggleSwitch`](../widgets/qtoggleswitch.md#superqt.switch.QStyleOptionToggleSwitch) | The style option that `QToggleSwitch` draws itself with (for subclasses). |
| [`MONTEREY_SLIDER_STYLES_FIX`](../faq.md#superqt.sliders.MONTEREY_SLIDER_STYLES_FIX) | A style sheet that works around a slider bug of Qt 5 on macOS 12+. |
