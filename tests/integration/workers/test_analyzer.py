from asyncio import create_task
from dataclasses import dataclass
from queue import Queue

from datek_web_crawler.modules.page_analyzer import PageAnalyzer
from datek_web_crawler.modules.page_store.s3 import S3PageStore
from datek_web_crawler.utils import run_in_threadpool
from datek_web_crawler.workers.analyzer import analyze_page


async def test_analyze_page(test_bucket, cleanup):
    # given
    path_queue: Queue[str] = Queue()
    new_paths_queue: Queue[str] = Queue()
    models_queue: Queue[Model] = Queue()

    path = "/recipe"
    test_bucket.put_object(
        Key=path,
        Body="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
    
</body>
</html>""",
    )

    # when
    analyze_task = create_task(
        run_in_threadpool(
            analyze_page,
            analyzer_class=DummyAnalyzer,
            page_store_class=S3PageStore,
            path_queue=path_queue,
            new_paths_queue=new_paths_queue,
            models_queue=models_queue,
        )
    )

    def _cleanup():
        analyze_task.cancel()
        path_queue.shutdown()
        new_paths_queue.shutdown()
        models_queue.shutdown()

    cleanup.func = _cleanup

    path_queue.put(path)

    # then
    assert (
        await run_in_threadpool(models_queue.get, timeout=0.5)
    ) == DummyAnalyzer.NEW_MODEL

    paths = {
        await run_in_threadpool(new_paths_queue.get, timeout=0.5) for _ in range(2)
    }

    assert paths == DummyAnalyzer.NEW_PATHS


@dataclass
class Model:
    content: str


class DummyAnalyzer(PageAnalyzer[Model]):
    NEW_PATHS = {"/cookie", "/soup"}
    NEW_MODEL = Model("recipe content")

    def get_model(self) -> Model | None:
        return self.NEW_MODEL

    def get_new_paths(self) -> set[str]:
        return self.NEW_PATHS
