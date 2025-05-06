from datek_web_crawler.modules.deduplicator.base import Deduplicator


class MemoryDeduplicator(Deduplicator):
    def __init__(self):
        self._cache: set[str] = set()

    def is_duplicate(self, item: str) -> bool:
        if item in self._cache:
            return True

        self._cache.add(item)
        return False
