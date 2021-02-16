import os
import sys
import types

from functools import partial

from tornado import process

from .callbacks import PeriodicCallback
from .state import state

_watched_files = set()

def autoreload_watcher():
    PeriodicCallback(callback=partial(_reload_on_update, {})).start()

def _reload():
    state.location.reload = True

def watch(filename):
    """Add a file to the watch list.

    All imported modules are watched by default.
    """
    _watched_files.add(filename)

def _check_file(modify_times, path):
    try:
        modified = os.stat(path).st_mtime
    except Exception:
        return
    if path not in modify_times:
        modify_times[path] = modified
        return
    if modify_times[path] != modified:
        _reload()

def _reload_on_update(modify_times):
    if process.task_id() is not None:
        # We're in a child process created by fork_processes.  If child
        # processes restarted themselves, they'd all restart and then
        # all call fork_processes again.
        return
    for module in list(sys.modules.values()):
        # Some modules play games with sys.modules (e.g. email/__init__.py
        # in the standard library), and occasionally this can cause strange
        # failures in getattr.  Just ignore anything that's not an ordinary
        # module.
        if not isinstance(module, types.ModuleType):
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        if path.endswith(".pyc") or path.endswith(".pyo"):
            path = path[:-1]
        _check_file(modify_times, path)
    for path in _watched_files:
        _check_file(modify_times, path)
