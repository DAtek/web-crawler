from asyncio import create_task
from queue import Empty, Queue

from pytest import raises

from datek_web_crawler.modules.deduplicator.memory import MemoryDeduplicator
from datek_web_crawler.utils import run_in_threadpool
from datek_web_crawler.workers.deduplicator import dedup


async def test_dedup(cleanup):
    # given
    q1: Queue[str] = Queue()
    q2: Queue[str] = Queue()

    dedup_task = create_task(
        run_in_threadpool(
            dedup,
            deduplicator_class=MemoryDeduplicator,
            in_queue=q1,
            out_queue=q2,
        )
    )

    def _cleanup():
        dedup_task.cancel()
        q1.shutdown()
        q2.shutdown()

    cleanup.func = _cleanup

    item = "https://demo.com/example"

    # when
    q1.put(item)
    q1.put(item)

    # then
    (await run_in_threadpool(q2.get, timeout=0.1)) == item

    with raises(Empty):
        await run_in_threadpool(q2.get, timeout=0.1)
