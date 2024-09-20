"""Utility Functions."""

import logging

from psycopg_async_listen.db import get_connection

_log = logging.getLogger(__name__)


# write a helper function that will execute the notification
# using a connection and cursor
async def help_send_notification(channel: str = "test_channel", payload: str = "test_payload"):
    async with get_connection() as conn:
        _log.debug("sending notification")
        await conn.execute("SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": payload})
