from abc import ABC, abstractmethod


class DownloadError(Exception):
    def __init__(
        self,
        status_code: int | None = None,
        content: str | None = None,
        original_error: Exception | None = None,
    ):
        self.status_code = status_code
        self.content = content
        self.original_error = original_error


class PageDownloader(ABC):
    @abstractmethod
    async def download(self, path: str) -> str: ...  # pragma: no cover
