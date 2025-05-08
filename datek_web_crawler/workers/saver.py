import asyncio
from asyncio import gather, run
from collections.abc import Callable
from os import getpid

from structlog import get_logger

from datek_web_crawler.modules.result_store import ResultStore
from datek_web_crawler.types import AsyncQueue, Queue
from datek_web_crawler.utils import from_sync_to_async_queue


def save[T](
    queue: Queue[T],
    result_store_class: type[ResultStore[T]],
    configure_logger: Callable | None = None,
):
    if configure_logger:
        configure_logger()

    logger = get_logger().bind(pid=getpid(), name="ResultSaver")
    logger.info("Started")
    run(_save(queue, result_store_class()))


async def _save[T](
    queue: Queue[T],
    result_store: ResultStore[T],
):
    async_queue: AsyncQueue[T] = asyncio.Queue()
    await gather(
        from_sync_to_async_queue(queue, async_queue),
        _save_results(async_queue, result_store),
        result_store.signal_stop(),
    )


async def _save_results[T](
    queue: AsyncQueue[T],
    result_store: ResultStore[T],
):
    while True:
        result = await queue.get()
        await result_store.save(result)
