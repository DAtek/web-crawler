from typing import Protocol

from datek_web_crawler.utils import async_proxy


class TestAsyncProxy:
    async def test_specified_methods_are_async(self):
        # given
        dummy = Dummy(5)
        async_dummy: AsyncDummy = async_proxy(dummy, {"add", "pow"})

        # then
        assert await async_dummy.add(1) == 6
        assert await async_dummy.pow(2) == 25
        assert async_dummy.multiply(2) == 10

    async def test_all_methods_are_async_if_methods_names_are_not_specified(self):
        # given
        dummy = Dummy(5)
        async_dummy: FullAsyncDummy = async_proxy(dummy)

        # then
        assert await async_dummy.add(1) == 6
        assert await async_dummy.pow(2) == 25
        assert await async_dummy.pow(2) == 25
        assert await async_dummy.multiply(2) == 10


class Dummy:
    def __init__(self, initial_value: int):
        self._initial_value = initial_value

    def add(self, val: int) -> int:
        return self._initial_value + val

    def pow(self, val: int) -> int:
        return self._initial_value**val

    def multiply(self, val: int) -> int:
        return self._initial_value * val


class AsyncDummy(Protocol):
    async def add(self, val: int) -> int: ...

    async def pow(self, val: int) -> int: ...

    def multiply(self, val: int) -> int: ...


class FullAsyncDummy(Protocol):
    async def add(self, val: int) -> int: ...

    async def pow(self, val: int) -> int: ...

    async def multiply(self, val: int) -> int: ...
