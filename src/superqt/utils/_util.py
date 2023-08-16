from __future__ import annotations

from inspect import signature
from typing import Callable


def get_max_args(func: Callable) -> int | None:
    """Return the maximum number of positional arguments that func can accept."""
    if not callable(func):
        raise TypeError(f"{func!r} is not callable")

    try:
        sig = signature(func)
    except Exception:
        return None

    max_args = 0
    for param in sig.parameters.values():
        if param.kind == param.VAR_POSITIONAL:
            return None
        if param.kind in {param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD}:
            max_args += 1
    return max_args
