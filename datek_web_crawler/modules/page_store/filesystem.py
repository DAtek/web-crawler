import lzma
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import quote_plus

from datek_web_crawler.modules.page_store.base import PageStore


class FilesystemPageStore(PageStore, ABC):
    def __init__(self):
        self.workdir().mkdir(parents=True, exist_ok=True)

    @classmethod
    @abstractmethod
    def workdir(cls) -> Path: ...  # pragma: no cover

    def put(self, key: str, content: str):
        compressed = lzma.compress(content.encode())
        self._file(key).write_bytes(compressed)

    def get(self, key: str) -> str | None:
        try:
            data = self._file(key).read_bytes()
        except FileNotFoundError:
            return None

        return lzma.decompress(data).decode()

    def exists(self, key: str) -> bool:
        return self._file(key).exists()

    def _file(self, key: str) -> Path:
        return self.workdir() / quote_plus(key)
