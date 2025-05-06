from abc import ABC, abstractmethod

from lxml import html
from lxml.html import HtmlElement


class PageAnalyzer[T](ABC):
    def __init__(self, content: str):
        self.html: HtmlElement = html.fromstring(content)

    @abstractmethod
    def get_model(self) -> T | None:  # pragma: no cover
        pass

    @abstractmethod
    def get_new_paths(self) -> set[str]:  # pragma: no cover
        pass
