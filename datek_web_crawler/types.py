from typing import Protocol


class Queue[T](Protocol):
    def put(self, item: T, block=True, timeout=None) -> None:  # pragma: no cover
        pass

    def get(self, block=True, timeout=None) -> T:  # pragma: no cover
        pass

    def qsize(self) -> int:  # pragma: no cover
        pass


class AsyncQueue[T](Protocol):
    async def put(self, item: T) -> None:  # pragma: no cover
        pass

    async def get(self) -> T:  # pragma: no cover
        pass

    def qsize(self) -> int:  # pragma: no cover
        pass


type StrQueue = Queue[str]
type AsyncStrQueue = AsyncQueue[str]
