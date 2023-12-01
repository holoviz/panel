import asyncio
import os
import tempfile

import pytest

from panel.io.location import Location
from panel.io.reload import (
    _check_file, _modules, _watched_files, async_file_watcher, in_denylist,
    record_modules, watch,
)
from panel.io.state import state
from panel.tests.util import async_wait_until


def test_record_modules_not_stdlib():
    with record_modules():
        import audioop  # noqa
    assert ((_modules == set()) or (_modules == set(['audioop'])))
    _modules.clear()

def test_check_file():
    modify_times = {}
    _check_file(__file__, modify_times)
    assert modify_times[__file__] == os.stat(__file__).st_mtime

def test_file_in_denylist():
    filepath = '/home/panel/lib/python/site-packages/panel/__init__.py'
    assert in_denylist(filepath)
    filepath = '/home/panel/.config/panel.py'
    assert in_denylist(filepath)
    filepath = '/home/panel/development/panel/__init__.py'
    assert not in_denylist(filepath)

def test_watch():
    filepath = os.path.abspath(__file__)
    watch(filepath)
    assert _watched_files == {filepath}
    # Cleanup
    _watched_files.clear()

@pytest.mark.flaky(reruns=3)
async def test_reload_on_update(server_document, stop_event):
    location = Location()
    state._locations[server_document] = location
    state._loaded[server_document] = True
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(b'Foo')
        temp.flush()
        watch(temp.name)
        task = asyncio.create_task(async_file_watcher(stop_event))
        await asyncio.sleep(0.51)
        temp.write(b'Bar')
        temp.flush()

        await async_wait_until(lambda: location.reload)
    del task

@pytest.mark.flaky(reruns=3)
async def test_reload_on_delete(server_document, stop_event):
    location = Location()
    state._locations[server_document] = location
    state._loaded[server_document] = True
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(b'Foo')
        temp.flush()
        watch(temp.name)
        task = asyncio.create_task(async_file_watcher(stop_event))

    await async_wait_until(lambda: location.reload)
    del task
