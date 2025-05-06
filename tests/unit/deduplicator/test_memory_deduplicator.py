from pytest import mark, param

from datek_web_crawler.modules.deduplicator.memory import MemoryDeduplicator


class TestMemoryDeduplicator:
    @mark.parametrize(
        ["iterations", "expected"],
        [
            param(1, False, id="item is new"),
            param(2, True, id="item is duplicate"),
        ],
    )
    def test_is_duplicate(self, iterations: int, expected: bool):
        # given
        deduplicator = MemoryDeduplicator()

        # when
        for _ in range(iterations):
            duplicate = deduplicator.is_duplicate("a")

        # then
        assert duplicate is expected
