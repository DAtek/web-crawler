from collections.abc import Callable
from os import getpid
from queue import Queue
from typing import Any

from structlog import get_logger

from datek_web_crawler.modules.page_analyzer import PageAnalyzer
from datek_web_crawler.modules.page_store.base import PageStore
from datek_web_crawler.types import StrQueue
from datek_web_crawler.utils import run_in_loop


def analyze_page(
    analyzer_class: type[PageAnalyzer],
    page_store_class: type[PageStore],
    path_queue: StrQueue,
    new_paths_queue: StrQueue,
    models_queue: StrQueue,
    configure_logger: Callable | None = None,
):
    if configure_logger:
        configure_logger()

    logger = get_logger().bind(pid=getpid(), name="Analyzer")
    logger.info("Worker started")
    page_store = page_store_class()
    f = run_in_loop(_analyze_page)

    f(
        analyzer_class=analyzer_class,
        path_queue=path_queue,
        new_paths_queue=new_paths_queue,
        models_queue=models_queue,
        page_store=page_store,
        logger=logger,
    )

    logger.info("Worker stopped")


def _analyze_page(
    analyzer_class: type[PageAnalyzer],
    path_queue: StrQueue,
    new_paths_queue: StrQueue,
    models_queue: Queue,
    page_store: PageStore,
    logger: Any,
):
    path = path_queue.get()
    content = page_store.get(path)

    if not content:
        logger.error("Content not found", path=path)
        return

    analyzer = analyzer_class(content)
    logger.info("Analyzing", path=path)
    try:
        for path in analyzer.get_new_paths():
            new_paths_queue.put(path)

        models_queue.put(analyzer.get_model())
    except (KeyboardInterrupt, BrokenPipeError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
