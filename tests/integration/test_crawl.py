from asyncio import CancelledError, sleep, timeout
from uuid import uuid4

import structlog
from pytest import raises

from datek_web_crawler.crawl import crawl
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


class StoppingResultStore(ResultStore[Dummy]):
    err_after = 0.3
    error_msg = "NUCLEAR MELTDOWN"
    err_class: type[BaseException] = CancelledError

    async def save(self, result: Dummy): ...

    async def signal_stop(self):
        await sleep(self.err_after)
        raise self.err_class(self.error_msg)


class BrokenResultStore(StoppingResultStore):
    err_class = Exception
