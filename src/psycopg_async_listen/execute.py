"""Main logic of the application."""

import asyncio
import logging

import psycopg

from psycopg_async_listen.db import get_connection

_log = logging.getLogger(__name__)


# create a callable class that will handle notifications but can configured
# with the queue to add the notifications to
class QueuePutNotifyHandler:
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    def callback(self, msg: psycopg.Notify):
        _log.debug("Received notification: %s from %s", msg.payload, msg.channel)
        asyncio.run_coroutine_threadsafe(self.queue.put(msg.payload), asyncio.get_event_loop())


# write function that will listen to notifications on a channel and add them to a queue
# this function will run indefinitely until:
# 1. the task is cancelled
# 2. the connection is closed
# 3. an exception is raised
async def listen_for_notifications(channel: str, queue: asyncio.Queue):
    """Listen for notifications on a channel and add them to a queue.

    :param channel: The channel to listen for notifications on.
    :param queue: The queue to add the notifications to.
    """
    notify_handler_factory = QueuePutNotifyHandler(queue)

    async with get_connection() as conn:
        await conn.execute(f"LISTEN {channel};")
        conn.add_notify_handler(notify_handler_factory.callback)

        while True:
            try:
                await conn.execute("SELECT 1;")
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                conn.remove_notify_handler(notify_handler_factory.callback)
                await conn.execute(f"UNLISTEN {channel};")
                break