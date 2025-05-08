from datek_web_crawler.modules.page_downloader.httpx_downloader import (
    HTTPXPageDownloader,
)


class DummyDownloader(HTTPXPageDownloader):
    @classmethod
    def base_url(cls) -> str:
        return "http://127.0.0.1/"
