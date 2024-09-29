"""Tasks to run concurrently."""

import asyncio
import datetime
import logging
from abc import ABC, abstractmethod
from typing import ClassVar

# Get the logger for this module
_log = logging.getLogger(__name__)

# Pomodoro timer expirement
#
# We're going to expirment with a Pomodoro Timer. A technique for working
# in short bursts of time and taking breaks. We'll use asyncio to run
# multiple timers concurrently.
#
# To allow expirmenting with inheritence, we'll create a base abastract class
# that defines the interface for a timer. Then we'll create a concrete class
# that implements the timer logic. Finally, we'll create a class that
# manages multiple timers concurrently.


# Base class for a timer
class AbstractTimer(ABC):
    """A base class for a timer."""

    _completion_template: ClassVar[str]

    def __init__(self, duration: float):
        """Initalize a timer with duration in minutes.

        :param duration: The duration in minutes
        """
        self._duration = duration

    @abstractmethod
    async def __call__(self) -> tuple[str, datetime.datetime, datetime.timedelta]:
        """Run the timer.

        :return: A tuple with the name of the timer, the start time, and the duration
        """
        pass


# We are going to cratea NamedTimer that will take a name in addition to the duration
# and will log the name of the timer when it starts and completes.
class NamedTimer(AbstractTimer):
    """A timer with a name."""

    def __init__(self, name: str, duration: float):
        """Initalize a named timer with duration in minutes.

        :param name: The name of the timer
        :param duration: The duration in minutes
        """
        super().__init__(duration)
        self._name = name

    async def __call__(self) -> tuple[str, datetime.datetime, datetime.timedelta]:
        """Run the timer.

        :return: A tuple with the name of the timer, the start time, and the duration
        """
        _log.info(f"Starting {self._name} for {self._duration} minutes")
        start_time = datetime.datetime.now()
        await asyncio.sleep(self._duration * 60.0)
        _log.info(f"{self._name.title()}'s {self._completion_template}")
        return self._name, start_time, datetime.timedelta(minutes=self._duration)


# Concrete class for Work session, configurable with duration
class WorkTimer(NamedTimer):
    """a work timer."""

    _completion_template = "work session complete"


# Concrete class for Break session, configurable with duration
class BreakTimer(NamedTimer):
    """A break timer."""

    _completion_template = "break session complete"


# To manager multiple timers concurrently, let's think of a scenario like a university library
# where students are studying, taking breaks, and working on assignments:
#
# 1. Harneet start studying at 4:05 PM and uses 20 minutes work sessions and 5 minutes breaks.
# 2. Ananya starts studying at 4:10 PM and uses 25 minutes work sessions and 5 minutes breaks.
#
# We'll create a coroutine that manages these timers concurrently. With Harneet starting first, and Ananya starting 5 minutes later.
# We'll not use asyncio.gather() to run the timers concurrently (because it hardly ever the right choice). Instead, we'll use
# asyncio.create_task() to run the timers concurrently.


# We are creaating async iterator that will yield alternating work and break timers
# for each student
class SessionIterator:
    """An async iterator that yields alternating work and break timers."""

    def __init__(self, name: str, work_duration: float, break_duration: float):
        """Initalize the session iterator.

        :param name: The name of the user
        :param work_duration: The duration of the work session in minutes
        :param break_duration: The duration of the break session in minutes
        """
        self._name = name
        self._work_duration = work_duration
        self._break_duration = break_duration
        self._next_timer_is_work = True

    def __aiter__(self) -> "SessionIterator":
        """Return the async iterator."""
        return self

    async def __anext__(self) -> NamedTimer:
        """Get the next timer.

        if _next_timer_is_work is True, return a work timer
        otherwise, return a break timer
        """
        if self._next_timer_is_work:
            self._next_timer_is_work = False
            return WorkTimer(self._name, self._work_duration)
        else:
            self._next_timer_is_work = True
            return BreakTimer(self._name, self._break_duration)


# Then, we are going to create a coroutine that will:
# - yield coroutine from async iterators
# - start a timer
# - at the end of the timer, yield from the async iterator another timer
# - repeat until the async iterator is exhausted, or interrupt or cancelled
async def run_session(name: str, work_duration: float, break_duration: float):
    """Run a session with alternating work and break timers.

    :param name: The name of the user
    :param work_duration: The duration of the work session in minutes
    :param break_duration: The duration of the break session in minutes
    """
    async for timer in SessionIterator(name, work_duration, break_duration):
        yield timer()

# Coroutine to run multiple session concurrently
async def run_sessions(delay: float = 5):
    """Run multiple sessions concurrently."""
    harneet = run_session("Harneet", 20, 5)
    ananya = run_session("Ananya", 25, 5)

    # create tasks for each session, include the 5 minute delay for Ananya
    # include  try statement to catch the CancelledError or KeyboardInterrupt
    try:
        _log.info("Starting Harneet's session")
        harneet_task = asyncio.create_task(harneet)
        _log.info(f"Waiting for {delay} minutes before starting Ananya's session")
        await asyncio.sleep(delay * 60.0)
        _log.info("Starting Ananya's session")
        ananya_task = asyncio.create_task(ananya)

        # wait for both tasks to complete
        await harneet_task
        await ananya_task
    except (asyncio.CancelledError, KeyboardInterrupt):
        harneet_task.cancel()
        ananya_task.cancel()
        await asyncio.gather(harneet_task, ananya_task, return_exceptions=True)


# Run the multiple sessions concurrently
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(run_sessions())
