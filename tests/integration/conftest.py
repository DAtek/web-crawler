from collections.abc import Callable, Iterator
from time import sleep

from boto3 import Session as BotoSession
from datek_app_utils.env_config.utils import validate_config
from pytest import fixture
from types_boto3_s3.service_resource import Bucket, S3ServiceResource

from datek_web_crawler.modules.page_store.s3 import AWSConfig


@fixture(scope="session")
def config() -> type[AWSConfig]:
    validate_config(AWSConfig)
    return AWSConfig


@fixture(scope="session")
def boto3_session() -> BotoSession:
    return BotoSession()


@fixture(scope="session")
def s3(boto3_session: BotoSession, config) -> S3ServiceResource:
    return boto3_session.resource("s3", endpoint_url=config.AWS_ENDPOINT_URL)


@fixture
def test_bucket(s3, config, monkeypatch) -> Iterator[Bucket]:
    bucket = s3.Bucket(config.CRAWLER_BUCKET_NAME)

    try:
        bucket.create(
            CreateBucketConfiguration={"LocationConstraint": config.AWS_DEFAULT_REGION}
        )
    except Exception as e:
        if "BucketAlreadyOwnedByYou" not in str(e):
            raise
        bucket.objects.all().delete()

    yield bucket
    _delete_bucket(bucket)


class Defer:
    def __init__(self):
        self.func: Callable | None = None


@fixture
def cleanup(event_loop) -> Iterator[Defer]:
    defer = Defer()
    yield defer
    if defer.func:
        defer.func()


def _delete_bucket(bucket: Bucket):
    bucket.objects.all().delete()
    try:
        bucket.delete()
    except Exception as e:
        if "BucketNotEmpty" in str(e):
            sleep(0.1)
            _delete_bucket(bucket)
