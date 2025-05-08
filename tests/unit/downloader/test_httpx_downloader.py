from http.client import BAD_REQUEST
from unittest.mock import AsyncMock, Mock, patch

from httpx import AsyncClient
from pytest import raises

from datek_web_crawler.modules.page_downloader.base import DownloadError
from tests.helpers import DummyDownloader


class TestHTTPXPageDownloader:
    async def test_raises_download_error_if_status_code_not_ok(self):
        # given
        client = DummyDownloader()

        response = Mock()
        response.status_code = BAD_REQUEST
        response.text = "you were stupid"

        with (
            patch.object(
                AsyncClient, AsyncClient.get.__name__, AsyncMock(return_value=response)
            ),
            raises(DownloadError) as exc_info,
        ):
            # when
            await client.download("/something")

        assert exc_info.value.status_code == response.status_code
        assert exc_info.value.content == response.text

    async def test_raises_download_error_if_something_unexpected_happens(self):
        # given
        client = DummyDownloader()
        error = RuntimeError("nuclear meltdown")

        with (
            patch.object(
                AsyncClient, AsyncClient.get.__name__, AsyncMock(side_effect=error)
            ),
            raises(DownloadError) as exc_info,
        ):
            # when
            await client.download("/something")

        assert exc_info.value.original_error is error
