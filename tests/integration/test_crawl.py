from asyncio import timeout
from threading import Thread
from time import sleep
from uuid import uuid4

import structlog
from pytest import raises

from datek_web_crawler.crawl import StopError, crawl
from datek_web_crawler.modules.deduplicator.memory import MemoryDeduplicator
from datek_web_crawler.modules.page_analyzer import PageAnalyzer
from datek_web_crawler.modules.page_downloader.base import PageDownloader
from datek_web_crawler.modules.page_store.s3 import S3PageStore
from datek_web_crawler.modules.result_store import ResultStore


def configure_logger():
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer(),
        ],
    )


class TestCrawl:
    async def test_crawl_stops_properly(self, test_bucket):
        async with timeout(StoppingResultStore.err_after + 0.5):
            await crawl(
                start_url="http://127.0.0.1",
                downloader_class=DummyPageDownloader,
                analyzer_class=DummyPageAnalyzer,
                page_store_class=S3PageStore,
                result_store_class=StoppingResultStore,
                deduplicator_class=MemoryDeduplicator,
                concurrent_requests=5,
                configure_logger=configure_logger,
            )

    async def test_crawl_handles_unexpected_error(self, test_bucket):
        with raises(Exception):
            await crawl(
                start_url="http://127.0.0.1",
                downloader_class=DummyPageDownloader,
                analyzer_class=DummyPageAnalyzer,
                page_store_class=S3PageStore,
                result_store_class=BrokenResultStore,
                deduplicator_class=MemoryDeduplicator,
                concurrent_requests=5,
            )


class Dummy: ...


class DummyPageDownloader(PageDownloader):
    async def download(self, path: str) -> str:
        return "content"


class DummyPageAnalyzer(PageAnalyzer[Dummy]):
    def get_model(self) -> Dummy | None:
        return Dummy()

    def get_new_paths(self) -> set[str]:
        return {"/path1", str(uuid4())}


class BrokenResultStore(ResultStore[Dummy]):
    err_class = Exception
    err_after = 0.3

    def __init__(self):
        self._stopping_thread: Thread | None = None
        self._err: Exception | None = None

    def save(self, result: Dummy):
        if not self._stopping_thread:
            self._stopping_thread = Thread(
                target=self._set_err,
                daemon=True,
            )
            self._stopping_thread.start()

        if self._err:
            raise self._err

    def _set_err(self):
        sleep(self.err_after)
        self._err = self.err_class()


class StoppingResultStore(BrokenResultStore):
    err_class = StopError
