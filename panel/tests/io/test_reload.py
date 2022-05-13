import os

from panel.io.location import Location
from panel.io.reload import (
     _check_file, _modules, _reload_on_update, _watched_files,
    in_blacklist, record_modules, watch
)
from panel.io.state import state


def test_record_modules_not_stdlib():
    with record_modules():
        import audioop # noqa
    assert (_modules == set() or _modules == set('audioop'))
    _modules.clear()

def test_check_file():
    modify_times = {}
    _check_file(modify_times, __file__)
    assert modify_times[__file__] == os.stat(__file__).st_mtime

def test_file_in_blacklist():
    filepath = '/home/panel/lib/python/site-packages/panel/__init__.py'
    assert in_blacklist(filepath)
    filepath = '/home/panel/.config/panel.py'
    assert in_blacklist(filepath)
    filepath = '/home/panel/development/panel/__init__.py'
    assert not in_blacklist(filepath)

def test_watch():
    filepath = os.path.abspath(__file__)
    watch(filepath)
    assert _watched_files == {filepath}
    # Cleanup
    _watched_files.clear()

def test_reload_on_update():
    location = Location()
    state._location = location
    filepath = os.path.abspath(__file__)
    watch(filepath)
    modify_times = {filepath: os.stat(__file__).st_mtime-1}
    _reload_on_update(modify_times)
    assert location.reload

    # Cleanup
    _watched_files.clear()
    state._location = None
