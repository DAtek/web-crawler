from abc import ABC, abstractmethod
from typing import Protocol

from datek_web_crawler.utils import async_proxy


class PageStore(ABC):
    @abstractmethod
    def put(self, key: str, content: str): ...  # pragma: no cover

    @abstractmethod
    def get(self, key: str) -> str | None: ...  # pragma: no cover

    @abstractmethod
    def exists(self, key: str) -> bool: ...  # pragma: no cover

    def async_page_store(self) -> "AsyncPageStore":
        return async_proxy(self, {"put", "get", "exists"})


class AsyncPageStore(Protocol):
    async def put(self, key: str, content: str): ...  # pragma: no cover

    async def get(self, key: str) -> str | None: ...  # pragma: no cover

    async def exists(self, key: str) -> bool: ...  # pragma: no cover
