from abc import abstractmethod

try:
    from httpx import AsyncClient
except ImportError:  # pragma: no cover
    print("Install the `httpx` extra")
    raise

from datek_web_crawler.modules.page_downloader.base import DownloadError, PageDownloader


class HTTPXPageDownloader(PageDownloader):
    def __init__(self):
        self._client = AsyncClient(
            base_url=self.base_url(),
            timeout=60,
            follow_redirects=True,
        )

    @classmethod
    @abstractmethod
    def base_url(cls) -> str: ...  # pragma: no cover

    async def download(self, path: str) -> str:
        try:
            resp = await self._client.get(path)
        except Exception as e:
            raise DownloadError(original_error=e)

        if resp.status_code >= 400:
            raise DownloadError(status_code=resp.status_code, content=resp.text)

        return resp.text
