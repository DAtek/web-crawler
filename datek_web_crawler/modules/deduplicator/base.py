from abc import ABC, abstractmethod


class Deduplicator(ABC):
    @abstractmethod
    def is_duplicate(self, item: str) -> bool: ...  # pragma: no cover
