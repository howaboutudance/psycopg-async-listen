"""Tests for muliple tasks's task module."""
import asyncio

import pytest

from multiple_tasks.task import SessionIterator, run_session, run_sessions, WorkTimer, BreakTimer

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

    # create task for run session
    task = asyncio.create_task(run_session(m_name, m_work_duration, m_break_duration))
    await task

    # sleep for 1 second
    await asyncio.sleep(1)

    task.cancel()
    await task

    assert task.done()