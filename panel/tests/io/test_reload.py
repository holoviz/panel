import asyncio
import importlib
import os
import pathlib
import sys
import tempfile

import pytest

from panel.io.location import Location
from panel.io.reload import (
    _check_file, _modules, _watched_files, in_denylist, record_modules, watch,
)
from panel.io.state import state
from panel.tests.util import async_wait_until


def test_record_modules_not_stdlib():
    old_modules = _modules.copy()
    with record_modules():
        import dis  # noqa
    assert _modules == old_modules
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

async def test_reload_on_update(server_document, watch_files):
    location = Location()
    state._locations[server_document] = location
    state._loaded[server_document] = True
    with tempfile.NamedTemporaryFile() as temp:
        # Write to file and wait for filesystem to perform write
        temp.write(b'Foo')
        temp.flush()
        await asyncio.sleep(0.1)

        watch_files(temp.name)
        await asyncio.sleep(0.1)

        temp.write(b'Bar')
        temp.flush()
        pathlib.Path(temp.name).touch()

        await async_wait_until(lambda: location.reload)


# On macOS the watcher can report changes for the whole directory, which may hide it.
@pytest.mark.xfail(
    reason="The autoreload watcher only watches the files known when it started",
    strict=sys.platform != "darwin",
)
async def test_reload_on_update_of_module_recorded_after_watching(server_document, watch_files, tmp_path):
    location = Location()
    state._locations[server_document] = location
    state._loaded[server_document] = True
    app = tmp_path / 'app.py'
    app.write_text('')
    module = tmp_path / 'reload_recorded_module.py'
    module.write_text('value = 1')

    watch_files(str(app))
    await asyncio.sleep(0.1)

    sys.path.insert(0, str(tmp_path))
    try:
        with record_modules():
            importlib.import_module('reload_recorded_module')
    finally:
        sys.path.remove(str(tmp_path))
    await asyncio.sleep(0.1)

    try:
        module.write_text('value = 2')
        await async_wait_until(lambda: location.reload, timeout=3000)
    finally:
        sys.modules.pop('reload_recorded_module', None)
