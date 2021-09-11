from concurrent.futures import Future
from typing import Callable, TypeVar, overload

from typing_extensions import Literal, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

@overload
def ensure_main_thread(
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
@overload
def ensure_main_thread(
    func: Callable[P, R],
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[P, R]: ...
@overload
def ensure_main_thread(
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, Future[R]]]: ...
@overload
def ensure_main_thread(
    func: Callable[P, R],
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[P, Future[R]]: ...
@overload
def ensure_object_thread(
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...
@overload
def ensure_object_thread(
    func: Callable[P, R],
    await_return: Literal[True],
    timeout: int = 1000,
) -> Callable[P, R]: ...
@overload
def ensure_object_thread(
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[[Callable[P, R]], Callable[P, Future[R]]]: ...
@overload
def ensure_object_thread(
    func: Callable[P, R],
    await_return: Literal[False] = False,
    timeout: int = 1000,
) -> Callable[P, Future[R]]: ...
