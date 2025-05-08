from asyncio import get_event_loop
from collections.abc import Callable
from concurrent.futures.process import ProcessPoolExecutor
from functools import partial, wraps
from typing import Any

from datek_web_crawler.types import AsyncQueue, Queue


async def run_in_threadpool[T](func: Callable[..., T], *args, **kwargs) -> T:
    func_ = partial(func, *args, **kwargs)
    loop = get_event_loop()
    return await loop.run_in_executor(None, func_)


async def run_in_processpool[T](
    pool: ProcessPoolExecutor, func: Callable[..., T], *args, **kwargs
) -> T:
    func_ = partial(func, *args, **kwargs)
    loop = get_event_loop()
    return await loop.run_in_executor(pool, func_)


def run_in_loop(f: Callable) -> Callable:
    @wraps(f)
    def wrapper(*args, **kwargs):
        while True:
            try:
                f(*args, **kwargs)
            except (KeyboardInterrupt, BrokenPipeError, EOFError):
                return

    return wrapper


def ignore_closed_event_loop(f: Callable):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise e

    return wrapper


@ignore_closed_event_loop
async def from_sync_to_async_queue[T](queue: Queue[T], async_queue: AsyncQueue[T]):
    while True:
        try:
            val = await run_in_threadpool(queue.get)
        except EOFError:
            return

        await async_queue.put(val)


@ignore_closed_event_loop
async def from_async_to_sync_queue[T](async_queue: AsyncQueue[T], queue: Queue[T]):
    while True:
        val = await async_queue.get()
        await run_in_threadpool(queue.put, val)


def async_proxy(base: Any, async_methods: set[str] | None = None) -> Any:
    return _AsyncProxy(base, async_methods)


class _AsyncProxy:
    def __init__(self, obj: Any, async_methods: set[str] | None = None):
        self._obj = obj
        self._async_methods = async_methods
        self._method_cache: dict[str, Callable] = {}

    def __getattr__(self, item: str) -> Any:
        if cached := self._method_cache.get(item):
            return cached

        if not self._async_methods or item in self._async_methods:
            return self._wrap_async(item)(getattr(self._obj, item))

        return getattr(self._obj, item)

    def _wrap_async(self, key: str) -> Callable:
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await run_in_threadpool(func, *args, **kwargs)

            self._method_cache[key] = wrapper
            return wrapper

        return decorator
