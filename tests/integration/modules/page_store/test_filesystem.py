from pathlib import Path
from urllib.parse import quote_plus

from pytest import fixture

from datek_web_crawler.modules.page_store.base import AsyncPageStore
from datek_web_crawler.modules.page_store.filesystem import (
    FilesystemPageStore,
)


class TestTempFolderPageStore:
    async def test_exists_true(self, tmp_path, page_store):
        # given
        key = "foo/bar"
        (tmp_path / quote_plus(key)).touch()

        # when
        exists = await page_store.exists(key)

        # then
        assert exists is True

    async def test_exists_false(self, page_store):
        assert await page_store.exists("nothing_here") is False

    async def test_put_and_get(self, tmp_path, page_store):
        # given
        key = "key"
        content = "hehe"

        # when
        await page_store.put(key, content)
        result = await page_store.get(key)

        # then
        assert result == content

    async def test_get_returns_none_if_no_result(self, page_store):
        assert await page_store.get("no!") is None


@fixture
def page_store(tmp_path) -> AsyncPageStore:
    class TmpFolderPageStore(FilesystemPageStore):
        @classmethod
        def workdir(cls) -> Path:
            return Path(tmp_path).resolve()

    return TmpFolderPageStore().async_page_store()
