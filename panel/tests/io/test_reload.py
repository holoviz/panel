import os

from panel.io.reload import (
    _check_file, _modules, _watched_files, in_denylist, record_modules, watch,
)


def test_record_modules_not_stdlib():
    with record_modules():
        import audioop  # noqa
    assert ((_modules == set()) or (_modules == set(['audioop'])))
    _modules.clear()

def test_check_file():
    modify_times = {}
    _check_file(modify_times, __file__)
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
