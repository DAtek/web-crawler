from datek_web_crawler.modules.page_store.base import PageStore

try:
    from boto3 import Session
    from datek_app_utils.env_config.base import BaseConfig
    from types_boto3_s3.service_resource import Bucket

except ImportError:  # pragma: no cover
    print("Install the `s3` extra")
    raise


class AWSConfig(BaseConfig):
    CRAWLER_BUCKET_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_ENDPOINT_URL: str | None = None


class S3PageStore(PageStore):
    def __init__(self):
        boto_session = Session()
        s3 = boto_session.resource("s3", endpoint_url=AWSConfig.AWS_ENDPOINT_URL)
        self._bucket: Bucket = s3.Bucket(AWSConfig.CRAWLER_BUCKET_NAME)

    def exists(self, key: str) -> bool:
        obj = self._bucket.Object(key)

        try:
            obj.get()
        except Exception as e:
            if "NoSuchKey" not in str(e):
                raise
            return False

        return True

    def put(self, key: str, content: str):
        self._bucket.put_object(
            Key=key,
            Body=content,
        )

    def get(self, key: str) -> str | None:
        obj = self._bucket.Object(key)

        try:
            res = obj.get()
        except Exception as e:
            if "NoSuchKey" not in str(e):
                raise
            return None

        return res["Body"].read().decode()
