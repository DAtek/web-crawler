from collections.abc import Callable
from os import getpid

from structlog import get_logger

from datek_web_crawler.modules.deduplicator.base import Deduplicator
from datek_web_crawler.types import StrQueue
from datek_web_crawler.utils import run_in_loop


def dedup(
    deduplicator_class: type[Deduplicator],
    in_queue: StrQueue,
    out_queue: StrQueue,
    configure_logger: Callable | None = None,
):
    if configure_logger:
        configure_logger()

    logger = get_logger().bind(pid=getpid(), name="URLDeduplicator")
    logger.info("Worker started")
    deduplicator = deduplicator_class()
    f = run_in_loop(_dedup)

    f(
        deduplicator=deduplicator,
        in_queue=in_queue,
        out_queue=out_queue,
    )

    logger.info("Worker stopped")


def _dedup(
    deduplicator: Deduplicator,
    in_queue: StrQueue,
    out_queue: StrQueue,
):
    item = in_queue.get()
    if not deduplicator.is_duplicate(item):
        out_queue.put(item)
