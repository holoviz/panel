import asyncio
import collections
import contextlib
import time

from types import TracebackType
from typing import Dict, Optional, Type

try:  # Python 3.7
    base = contextlib.AbstractAsyncContextManager
    _current_task = asyncio.current_task
except AttributeError:
    base = object  # type: ignore
    _current_task = asyncio.Task.current_task  # type: ignore

class AsyncLeakyBucket(base):
    """A leaky bucket rate limiter.

    Allows up to max_rate / time_period acquisitions before blocking.

    time_period is measured in seconds; the default is 60.

    """
    def __init__(
        self,
        max_rate: float,
        time_period: float = 60,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self._loop = loop
        self._max_level = max_rate
        self._rate_per_sec = max_rate / time_period
        self._level = 0.0
        self._last_check = 0.0
        # queue of waiting futures to signal capacity to
        self._waiters: Dict[asyncio.Task, asyncio.Future] = collections.OrderedDict()

    def _leak(self) -> None:
        """Drip out capacity from the bucket."""
        if self._level:
            # drip out enough level for the elapsed time since
            # we last checked
            elapsed = time.time() - self._last_check
            decrement = elapsed * self._rate_per_sec
            self._level = max(self._level - decrement, 0)
        self._last_check = time.time()

    def has_capacity(self, amount: float = 1) -> bool:
        """Check if there is enough space remaining in the bucket"""
        self._leak()
        requested = self._level + amount
        # if there are tasks waiting for capacity, signal to the first
        # there there may be some now (they won't wake up until this task
        # yields with an await)
        if requested < self._max_level:
            for fut in self._waiters.values():
                if not fut.done():
                    fut.set_result(True)
                    break
        return self._level + amount <= self._max_level

    async def acquire(self, amount: float = 1) -> None:
        """Acquire space in the bucket.

        If the bucket is full, block until there is space.

        """
        if amount > self._max_level:
            raise ValueError("Can't acquire more than the bucket capacity")

        loop = self._loop or asyncio.get_event_loop()
        task = _current_task(loop)
        assert task is not None
        while not self.has_capacity(amount):
            # wait for the next drip to have left the bucket
            # add a future to the _waiters map to be notified
            # 'early' if capacity has come up
            fut = loop.create_future()
            self._waiters[task] = fut
            try:
                await asyncio.wait_for(
                    asyncio.shield(fut),
                    1 / self._rate_per_sec * amount,
                    loop=loop
                )
            except asyncio.TimeoutError:
                pass
            fut.cancel()
        self._waiters.pop(task, None)

        self._level += amount

        return None

    async def __aenter__(self) -> None:
        await self.acquire()
        return None

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType]
    ) -> None:
        return None
