from abc import ABC, abstractmethod


class ResultStore[T](ABC):
    @abstractmethod
    def save(self, result: T): ...  # pragma: no cover
