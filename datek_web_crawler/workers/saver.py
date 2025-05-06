from collections.abc import Callable
from functools import wraps
from os import getpid
from queue import Queue

from structlog import get_logger

from datek_web_crawler.modules.result_store import ResultStore
from datek_web_crawler.utils import run_in_loop


def save[T](
    queue: Queue[T],
    result_store_class: type[ResultStore[T]],
    configure_logger: Callable | None = None,
):
    if configure_logger:
        configure_logger()

    logger = get_logger().bind(pid=getpid(), name="ModelSaver")
    logger.info("Worker started")
    result_saver = result_store_class()
    f = _save_decorator(result_saver.save)
    f = run_in_loop(f)
    f(queue)
    logger.info("Worker stopped")


def _save_decorator[T](f: Callable):
    @wraps(f)
    def wrapper(queue: Queue[T]):
        item: T = queue.get()
        f(item)

    return wrapper
