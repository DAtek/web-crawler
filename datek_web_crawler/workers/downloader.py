import asyncio
from asyncio import gather
from typing import Any

from structlog import get_logger

from datek_web_crawler.modules.page_downloader.base import DownloadError, PageDownloader
from datek_web_crawler.modules.page_store.base import AsyncPageStore, PageStore
from datek_web_crawler.types import AsyncStrQueue, StrQueue
from datek_web_crawler.utils import (
    from_async_to_sync_queue,
    from_sync_to_async_queue,
    ignore_closed_event_loop,
)


async def download(
    page_store_class: type[PageStore],
    page_downloader_class: type[PageDownloader],
    paths_to_collect: StrQueue,
    downloaded_paths: StrQueue,
    concurrent_requests=50,
):
    async_paths_to_collect: AsyncStrQueue = asyncio.Queue()
    async_downloaded_paths: AsyncStrQueue = asyncio.Queue()
    page_store = page_store_class()
    async_page_store = page_store.async_page_store()
    page_downloader = page_downloader_class()
    f = ignore_closed_event_loop(_download_in_loop)

    await gather(
        *[
            from_sync_to_async_queue(paths_to_collect, async_paths_to_collect),
            from_async_to_sync_queue(async_downloaded_paths, downloaded_paths),
            *[
                f(
                    page_store=async_page_store,
                    page_downloader=page_downloader,
                    paths_to_collect=async_paths_to_collect,
                    downloaded_paths=async_downloaded_paths,
                    logger_=get_logger().bind(name=f"PageDownloader_{i}"),
                )
                for i in range(concurrent_requests)
            ],
        ]
    )


async def _download_in_loop(
    page_store: AsyncPageStore,
    page_downloader: PageDownloader,
    paths_to_collect: AsyncStrQueue,
    downloaded_paths: AsyncStrQueue,
    logger_: Any,
):
    while True:
        path = await paths_to_collect.get()
        _logger = logger_.bind(path=path)
        if await page_store.exists(path):
            _logger.info("Already downloaded")
            await downloaded_paths.put(path)
            continue

        _logger.info("Downloading")
        try:
            content = await page_downloader.download(path)
        except DownloadError as e:
            kwargs = {key: value for key, value in e.__dict__.items() if value}
            _logger.error("Unexpected download error", **kwargs)
            continue

        await page_store.put(path, content)
        await downloaded_paths.put(path)
