import asyncio
import multiprocessing
from asyncio import CancelledError, gather
from collections.abc import Callable
from concurrent.futures.process import ProcessPoolExecutor

from structlog import get_logger

from datek_web_crawler.modules.deduplicator.base import Deduplicator
from datek_web_crawler.modules.deduplicator.memory import MemoryDeduplicator
from datek_web_crawler.modules.page_analyzer import PageAnalyzer
from datek_web_crawler.modules.page_downloader.base import PageDownloader
from datek_web_crawler.modules.page_downloader.httpx_downloader import (
    HTTPXPageDownloader,
)
from datek_web_crawler.modules.page_store.base import PageStore
from datek_web_crawler.modules.result_store import ResultStore
from datek_web_crawler.types import AsyncQueue, Queue, StrQueue
from datek_web_crawler.utils import from_sync_to_async_queue, run_in_processpool
from datek_web_crawler.workers.analyzer import analyze_page
from datek_web_crawler.workers.deduplicator import dedup
from datek_web_crawler.workers.downloader import download
from datek_web_crawler.workers.saver import save
from datek_web_crawler.workers.status_logger import log_status


async def crawl[T](
    start_url: str,
    analyzer_class: type[PageAnalyzer[T]],
    page_store_class: type[PageStore],
    result_store_class: type[ResultStore[T]],
    downloader_class: type[PageDownloader] = HTTPXPageDownloader,
    deduplicator_class: type[Deduplicator] = MemoryDeduplicator,
    concurrent_requests=50,
    configure_logger: Callable | None = None,
):
    if configure_logger:
        configure_logger()

    mp_context = multiprocessing.get_context("spawn")
    with (
        mp_context.Manager() as manager,
        ProcessPoolExecutor(mp_context=mp_context) as pool,
    ):
        paths_to_collect: StrQueue = manager.Queue()
        downloaded_paths: StrQueue = manager.Queue()
        new_paths: StrQueue = manager.Queue()
        results: Queue[T] = manager.Queue()
        async_results: AsyncQueue[T] = asyncio.Queue()
        paths_to_collect.put(start_url)

        coroutines = [
            download(
                page_downloader_class=downloader_class,
                page_store_class=page_store_class,
                paths_to_collect=paths_to_collect,
                downloaded_paths=downloaded_paths,
                concurrent_requests=concurrent_requests,
            ),
            from_sync_to_async_queue(results, async_results),
            log_status(paths_to_collect, downloaded_paths),
            run_in_processpool(
                pool,
                save,
                queue=results,
                result_store_class=result_store_class,
                configure_logger=configure_logger,
            ),
            run_in_processpool(
                pool,
                dedup,
                in_queue=new_paths,
                out_queue=paths_to_collect,
                deduplicator_class=deduplicator_class,
                configure_logger=configure_logger,
            ),
        ]

        for _ in range(max(1, multiprocessing.cpu_count() - 3)):
            coroutines.append(
                run_in_processpool(
                    pool,
                    analyze_page,
                    analyzer_class=analyzer_class,
                    page_store_class=page_store_class,
                    path_queue=downloaded_paths,
                    new_paths_queue=new_paths,
                    models_queue=results,
                    configure_logger=configure_logger,
                )
            )

        try:
            await gather(*coroutines)
        except CancelledError:
            get_logger().info("Crawler stopped")
            pool.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            get_logger().error("Unexpected error", error=e)
            pool.shutdown(wait=False, cancel_futures=True)
            raise
