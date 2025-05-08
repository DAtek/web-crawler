from abc import ABC, abstractmethod


class ResultStore[T](ABC):
    async def signal_stop(self):
        """Should raise CancelledError to stop crawling"""
        pass

    @abstractmethod
    async def save(self, result: T): ...  # pragma: no cover
