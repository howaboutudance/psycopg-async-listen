"""Try to send notifications for end-to-end testing."""

import asyncio
import logging

from psycopg_async_listen.util import help_send_notification

_log = logging.getLogger(__name__)


async def main():
    for i in range(10):
        await help_send_notification("test_channel", f"test_payload_{i}")
        _log.debug("sent notification %s", i)
        await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
