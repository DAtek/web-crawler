from asyncio import create_task, sleep
from dataclasses import dataclass
from queue import Queue

from datek_web_crawler.modules.result_store import ResultStore
from datek_web_crawler.utils import run_in_threadpool
from datek_web_crawler.workers.saver import save


async def test_models_are_being_saved_into_db(cleanup):
    # given
    q: Queue[Recipe] = Queue()
    recipe_name = "cheesecake"

    # when
    q.put(Recipe(name=recipe_name))
    saver_task = create_task(
        run_in_threadpool(
            save,
            queue=q,
            result_store_class=DummyResultStore,
        )
    )

    def _cleanup():
        saver_task.cancel()
        q.shutdown()

    cleanup.func = _cleanup
    await sleep(0.1)

    # then
    assert DummyResultStore.recipes


@dataclass
class Recipe:
    name: str


class DummyResultStore(ResultStore[Recipe]):
    recipes: list[Recipe] = []

    def save(self, result: Recipe):
        self.recipes.append(result)
