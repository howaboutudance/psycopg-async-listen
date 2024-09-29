"""Test for async listen for notifications."""

import asyncio
from unittest import mock

import psycopg
import psycopg.sql
import pytest

from psycopg_async_listen.execute import listen_for_notifications
from psycopg_async_listen.util import help_send_notification


# write an integration test that uses two client connections to:
# 1. listen for notifications that are added to a queue
# 2. execute a notification
# 3. assert the notification sent is in the queue
@pytest.mark.integration
@pytest.mark.asyncio
async def test_intg_listen_for_notifications():
    # create a queue to hold the notifications
    m_queue = asyncio.Queue()

    m_channel = "test_channel"
    m_payload = "test_payload"

    # create a task to listen for notifications, timeout if after 5 seconds
    listen_task = asyncio.create_task(listen_for_notifications(m_channel, m_queue))

    async def run_test_task(queue, listening_task):
        try:
            # wait for the listening task to start listening
            await asyncio.sleep(0.1)

            # send a notification
            await help_send_notification(m_channel, m_payload)

            # wait for the notification to be added to the queue
            await asyncio.sleep(0.1)

            result = await asyncio.wait_for(queue.get(), timeout=1)
            assert result == m_payload

        finally:
            # cancel the listening task
            listening_task.cancel()
            await listening_task

    # run the test task but timeout after 5 seconds
    try:
        await asyncio.wait_for(run_test_task(m_queue, listen_task), timeout=10)
    except asyncio.TimeoutError:
        assert False, "Test timed out"


# assert get_connection was called
@pytest.mark.asyncio
async def test_listen_for_notifications_handlers():
    with (
        mock.patch("psycopg_async_listen.execute.get_connection") as m_get_connection,
        mock.patch("psycopg_async_listen.db.psycopg.AsyncConnection.add_notify_handler") as m_add_notify_handler,
        mock.patch("psycopg_async_listen.db.psycopg.AsyncConnection.remove_notify_handler") as m_remove_notify_handler,
    ):
        m_queue = asyncio.Queue()
        m_channel = "test_channel"

        m_get_connection.return_value.__aenter__.return_value = mock.AsyncMock(spec=psycopg.AsyncConnection)

        m_handlers = []
        m_add_notify_handler.side_effect = lambda x: m_handlers.append(x)
        m_remove_notify_handler.return_value = mock.AsyncMock()

        # since listen_for_notifications is a coroutine with a infinite loop
        # we ned to run it in a task and cancel after a short time
        listening_task = asyncio.create_task(listen_for_notifications(m_channel, m_queue))

        # wait for the listening task to start listening
        await asyncio.sleep(0.1)

        for handler in m_handlers:
            handler(psycopg.Notify(m_channel, "test_payload", 0))

        # cancel the listening task
        listening_task.cancel()
        try:
            await listening_task
        except asyncio.CancelledError:
            pass

        # assert get_connection was called
        assert m_get_connection.call_count == 1

        m_context_manager = m_get_connection.return_value.__aenter__

        # assert the connection was used correctly
        assert m_context_manager.call_count == 1
        assert m_context_manager.return_value.add_notify_handler.call_count == 1
        assert m_context_manager.return_value.execute.call_count >= 1
        assert m_context_manager.return_value.remove_notify_handler.call_count == 1
