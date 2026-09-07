"""Tests for PeriodicCallback's loop-driven path.

`_async_repeat` is the branch `start()` takes when there is a running event loop but
no bokeh session: Pyodide and WASM, notebooks, and scripts. Session-scoped callbacks
go to `doc.add_periodic_callback` instead and are covered in `panel/tests/test_server.py`.
"""

import asyncio
import time

import pytest

from panel.io.callbacks import PeriodicCallback


class _Stop(Exception):
    """Raised by a test callback to end the otherwise infinite `_async_repeat` loop."""


async def _drive(period, frames, body):
    """Run `_async_repeat` for `frames` iterations of `body`, counting loop turns.

    Returns (number of callback invocations, number of times a competing task ran).
    A competing task can only advance when `_async_repeat` suspends, so the second
    number is how many times the loop handed control back to the scheduler.
    """
    turns = 0

    async def competing():
        nonlocal turns
        while True:
            turns += 1
            await asyncio.sleep(0)

    calls = 0

    async def callback():
        nonlocal calls
        calls += 1
        body()
        if calls >= frames:
            raise _Stop

    competitor = asyncio.create_task(competing())
    await asyncio.sleep(0)

    cb = PeriodicCallback(callback=callback, period=period)
    try:
        with pytest.raises(_Stop):
            await cb._async_repeat(callback)
    finally:
        competitor.cancel()
    return calls, turns


async def test_overrunning_callback_still_yields_to_the_loop():
    frames = 5
    # 5 ms of work against a 1 ms period, so every frame overruns and the remaining
    # sleep budget is negative.
    calls, turns = await _drive(period=1, frames=frames, body=lambda: time.sleep(0.005))

    assert calls == frames
    assert turns >= frames


async def test_callback_inside_its_period_still_waits():
    start = time.monotonic()
    calls, _ = await _drive(period=50, frames=2, body=lambda: None)
    elapsed = time.monotonic() - start

    assert calls == 2
    assert elapsed >= 0.03
