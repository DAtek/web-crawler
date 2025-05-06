try:
    from httpx import AsyncClient
except ImportError:  # pragma: no cover
    print("Install the `httpx` extra")
    raise

from datek_web_crawler.modules.page_downloader.base import DownloadError, PageDownloader


class HTTPXPageDownloader(PageDownloader):
    BASE_URL: str

    def __init__(self):
        self._client = self._init_client()

    def _init_client(self) -> AsyncClient:
        return AsyncClient(
            timeout=30,
            follow_redirects=True,
            base_url=self.BASE_URL.removesuffix("/"),
        )

    async def download(self, path: str) -> str:
        try:
            resp = await self._client.get(path)
        except Exception as e:
            raise DownloadError(original_error=e)

        if resp.status_code >= 400:
            raise DownloadError(status_code=resp.status_code, content=resp.text)

        return resp.text
