from collections.abc import Iterator
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from pytest import fixture


@fixture
def mocked_httpx_get() -> Iterator[AsyncMock]:
    mock = AsyncMock()
    with patch.object(AsyncClient, AsyncClient.get.__name__, mock):
        yield mock
