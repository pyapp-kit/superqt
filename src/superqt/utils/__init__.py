from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from superqt.cmap import draw_colormap

__all__ = (
    "CodeSyntaxHighlight",
    "FunctionWorker",
    "GeneratorWorker",
    "QFlowLayout",
    "QMessageHandler",
    "QSignalDebouncer",
    "QSignalThrottler",
    "WorkerBase",
    "create_worker",
    "draw_colormap",
    "ensure_main_thread",
    "ensure_object_thread",
    "exceptions_as_dialog",
    "new_worker_qthread",
    "qdebounced",
    "qimage_to_array",
    "qthrottled",
    "signals_blocked",
    "thread_worker",
)

from ._code_syntax_highlight import CodeSyntaxHighlight
from ._ensure_thread import ensure_main_thread, ensure_object_thread
from ._errormsg_context import exceptions_as_dialog
from ._flow_layout import QFlowLayout
from ._img_utils import qimage_to_array
from ._message_handler import QMessageHandler
from ._misc import signals_blocked
from ._qthreading import (
    FunctionWorker,
    GeneratorWorker,
    WorkerBase,
    create_worker,
    new_worker_qthread,
    thread_worker,
)
from ._throttler import QSignalDebouncer, QSignalThrottler, qdebounced, qthrottled


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name == "draw_colormap":
        from superqt.cmap import draw_colormap

        return draw_colormap
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
