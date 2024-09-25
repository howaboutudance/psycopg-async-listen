"""Utility Functions."""
import asyncio
import logging
import uuid

from psycopg_async_listen.db import get_connection

_log = logging.getLogger(__name__)


# write a helper function that will execute the notification
# using a connection and cursor
async def help_send_notification(channel: str = "test_channel", payload: str = "test_payload"):
    async with get_connection() as conn:
        _log.debug("sending notification")
        await conn.execute("SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": payload})
    
async def help_send_notifcations_continuously(channel: str = "test_channel", payload: str = "test_payload"):
    """Send notifications continuously until keyboard interrupt."""
    async with get_connection() as conn:
        while True:
            try:
                # generate a random uuid to append to the payload
                payload_count = str(uuid.uuid4().hex)
                payload_msg = f"{payload}-{payload_count}"
                await conn.execute("SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": payload_msg})
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                # send notify with a stop payload
                await conn.execute("SELECT pg_notify (%(channel)s, %(payload)s)", {"channel": channel, "payload": "stop"})
                break
