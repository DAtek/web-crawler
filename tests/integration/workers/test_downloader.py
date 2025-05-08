from asyncio import create_task, sleep, timeout
from http.client import OK
from queue import Queue
from unittest.mock import Mock

from datek_web_crawler.modules.page_store.s3 import S3PageStore
from datek_web_crawler.utils import run_in_threadpool
from datek_web_crawler.workers.downloader import download
from tests.helpers import DummyDownloader


async def test_download(test_bucket, mocked_httpx_get, cleanup):
    # given
    response = Mock()
    response.status_code = OK
    response.text = "asd"
    mocked_httpx_get.return_value = response
    paths = ["/a", "/b"]
    paths_to_collect: Queue[str] = Queue()
    for path in paths:
        paths_to_collect.put(path)

    downloaded_paths: Queue[str] = Queue()

    # when
    download_task = create_task(
        download(
            page_store_class=S3PageStore,
            page_downloader_class=DummyDownloader,
            paths_to_collect=paths_to_collect,
            downloaded_paths=downloaded_paths,
            concurrent_requests=10,
        )
    )

    def _cleanup():
        download_task.cancel()
        paths_to_collect.shutdown()
        downloaded_paths.shutdown()

    cleanup.func = _cleanup

    # then
    downloaded_paths_list: list[str] = []

    async def check_downloaded_paths():
        nonlocal downloaded_paths_list
        while len(downloaded_paths_list) < 2:
            downloaded_paths_list.append(await run_in_threadpool(downloaded_paths.get))
            await sleep(0.1)

    async with timeout(2):
        await check_downloaded_paths()

    # contents have been saved
    for path in paths:
        resp = test_bucket.Object(key=path).get()
        assert resp["Body"].read().decode() == response.text
