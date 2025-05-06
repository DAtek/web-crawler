from pytest import fixture, raises

from datek_web_crawler.modules.page_store.base import AsyncPageStore
from datek_web_crawler.modules.page_store.s3 import S3PageStore


class TestS3PageStore:
    async def test_exists_true(self, test_bucket, page_store):
        # given
        key = "https://some-url/path"
        obj = test_bucket.Object(key)
        obj.put(Body="haha")

        # when
        exists = await page_store.exists(key)

        # then
        assert exists is True

    async def test_exists_false(self, test_bucket, page_store):
        # when
        exists = await page_store.exists("nothing_here")

        # then
        assert exists is False

    async def test_exists_raises_exception_if_bucket_not_exists(self, page_store):
        # when
        with raises(Exception) as exc_info:
            await page_store.exists("nothing_here")

        # then
        assert "NoSuchBucket" in str(exc_info.value)

    async def test_put(self, test_bucket, page_store):
        # given
        key = "key"
        content = "content"

        # when
        await page_store.put(key, content)

        # then
        obj = test_bucket.Object(key)
        assert obj.get()["Body"].read().decode() == content

    async def test_get_returns_result(self, test_bucket, page_store):
        # given
        key = "key"
        obj = test_bucket.Object(key)
        body = "hehe"
        obj.put(Body=body)

        # when
        result = await page_store.get(key)

        # then
        assert result == body

    async def test_get_returns_none_if_no_result(self, test_bucket, page_store):
        # when
        result = await page_store.get("nope")

        # then
        assert result is None

    async def test_get_raises_exception_if_bucket_not_exists(self, page_store):
        # when
        with raises(Exception) as exc_info:
            await page_store.get("nothing_here")

        # then
        assert "NoSuchBucket" in str(exc_info.value)


@fixture(scope="session")
def page_store() -> AsyncPageStore:
    s3_store = S3PageStore()
    return s3_store.async_page_store()
