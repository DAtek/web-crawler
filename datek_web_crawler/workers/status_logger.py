from asyncio import sleep

from structlog import get_logger

from datek_web_crawler.types import StrQueue


async def log_status(
    paths_to_collect: StrQueue,
    downloaded_paths: StrQueue,
):
    logger = get_logger().bind(name="StatusLogger")
    while True:
        logger.info(
            "Status",
            paths_to_collect_size=paths_to_collect.qsize(),
            downloaded_paths_size=downloaded_paths.qsize(),
        )
        await sleep(2)
