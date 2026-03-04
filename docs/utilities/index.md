# Utilities

## Font Icons

| Object                          | Description           |
| -----------                     | --------------------- |
| [`addFont`](./fonticon.md#superqt.fonticon.addFont) | Add an `OTF/TTF` file at to the font registry. |
| [`font`](./fonticon.md#superqt.fonticon.font) | Create `QFont` for a given font-icon font family key |
| [`icon`](./fonticon.md#superqt.fonticon.icon) | Create a `QIcon` for font-con glyph key |
| [`setTextIcon`](./fonticon.md#superqt.fonticon.setTextIcon) | Set text on a `QWidget` to a specific font & glyph. |
| [`IconFont`](./fonticon.md#superqt.fonticon.IconFont) | Helper class that provides a standard way to create an `IconFont`. |
| [`IconOpts`](./fonticon.md#superqt.fonticon.IconOpts) | Options for rendering an icon |
| [`Animation`](./fonticon.md#superqt.fonticon.Animation) | Base class for adding animations to a font-icon. |

## SVG Icons

| Object                          | Description           |
| -----------                     | --------------------- |
| [`QIconifyIcon`](./iconify.md)  | QIcons backed by the [Iconify](https://iconify.design/) icon library. |

## Threading tools

| Object                          | Description           |
| -----------                     | --------------------- |
| [`ensure_main_thread`](./thread_decorators.md#ensure_main_thread)        | Decorator that ensures a function is called in the main `QApplication` thread. |
| [`ensure_object_thread`](./thread_decorators.md#ensure_object_thread)      | Decorator that ensures a `QObject` method is called in the object's thread. |
| [`FunctionWorker`](./threading.md#superqt.utils.FunctionWorker)      | `QRunnable` with signals that wraps a simple long-running function. |
| [`GeneratorWorker`](./threading.md#superqt.utils.GeneratorWorker)      | `QRunnable` with signals that wraps a long-running generator. |
| [`create_worker`](./threading.md#superqt.utils.create_worker)      | Create a worker to run a target function in another thread. |
| [`thread_worker`](./threading.md#superqt.utils.thread_worker)      | Decorator for `create_worker`, turn a function into a worker. |

## Miscellaneous

| Object                          | Description           |
| -----------                     | --------------------- |
| [`QMessageHandler`](./qmessagehandler.md)           | A context manager to intercept messages from Qt. |
| [`CodeSyntaxHighlight`](./code_syntax_highlight.md) | A `QSyntaxHighlighter` for code syntax highlighting. |
| [`draw_colormap`](./cmap.md) | Function that draws a colormap into any QPaintDevice. |
