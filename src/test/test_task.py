"""Tests for muliple tasks's task module."""

import asyncio
from unittest import mock

import pytest

from multiple_tasks.task import (
    BreakTimer,
    NamedTimer,
    SessionIterator,
    WorkTimer,
    run_session,
    run_sessions,
)

# test work timer, set duration to 1 second
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "m_timer_type, m_timer_name",
    [
        (WorkTimer, "Work"),
        (BreakTimer, "Break"),
    ],
)
async def test_work_timer(m_timer_type, m_timer_name):
    """Test the work timer."""
    # create timer with 1 second duration
    timer = m_timer_type(m_timer_name, 0.1)

    # create task for timer assert completed
    task = asyncio.create_task(timer())
    await task

    assert task.done()

    assert timer._name == m_timer_name
    assert timer._duration == 0.1


# test session iterator
@pytest.mark.asyncio
async def test_session_iterator():
    """Test the session iterator."""
    m_timer_name = "Test"

    # create session iterator
    session = SessionIterator(m_timer_name, 0.1, 0.1)

    # get work timer
    timer = await session.__anext__()
    assert isinstance(timer, WorkTimer)
    assert timer._name == m_timer_name
    assert timer._duration == 0.1

    assert session.__aiter__() == session

    # get break timer
    timer = await session.__anext__()
    assert isinstance(timer, BreakTimer)
    assert timer._name == m_timer_name
    assert timer._duration == 0.1


# test run session, with work duration of 1 second and break duration of 1 second
@pytest.mark.asyncio
async def test_run_session():
    """Test the run session."""
    m_name = "Test"
    m_work_duration = 0.1
    m_break_duration = 0.1

    class TestTimer(NamedTimer):
        _completion_template = "test session complete"

    class TestSessionIterator(SessionIterator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # in test classes, we assert object variables
            assert self._name == m_name
            assert self._work_duration == m_work_duration
            assert self._break_duration == m_break_duration
            self._count = 0

        async def __anext__(self):
            if self._count == 0:
                self._count += 1
                return TestTimer(self._name, self._work_duration)
            else:
                raise StopAsyncIteration

    with mock.patch("multiple_tasks.task.SessionIterator", new=TestSessionIterator):
        # create task for run session
        task = asyncio.create_task(run_session(m_name, m_work_duration, m_break_duration))

        await asyncio.sleep(0.1)
        await asyncio.wait_for(task, timeout=10)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert task.done()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "m_exception, should_cancel",
    [
        (asyncio.CancelledError, True),
        (None, False),
    ],
)
async def test_run_sessions(m_exception, should_cancel, caplog):
    """Test the run sessions."""
    # set log level to info
    caplog.set_level(10)
    with (
        mock.patch("multiple_tasks.task.run_session") as m_run_session,
    ):
        if should_cancel:
            m_run_session.side_effect = m_exception

        _ = await run_sessions(0.1)

        assert m_run_session.call_count == 2
        assert "Starting Harneet's session" in caplog.text
        assert "Waiting for 0.1 minutes before starting Ananya's session" in caplog.text
        assert "Starting Ananya's session" in caplog.text
