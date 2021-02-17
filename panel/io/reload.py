import os
import sys
import types

from functools import partial

from .callbacks import PeriodicCallback
from .state import state


_watched_files = set()
_modules = set()
_callbacks = {}

def autoreload_watcher():
    """
    Installs a periodic callback which checks for changes in watched
    files and sys.modules.
    """
    cb = partial(_reload_on_update, {})
    _callbacks[state.curdoc] = pcb = PeriodicCallback(callback=cb)
    pcb.start()

def watch(filename):
    """
    Add a file to the watch list.

    All imported modules are watched by default.
    """
    _watched_files.add(filename)

def record_modules():
    """
    Records modules which are currently imported.
    """
    _modules.update(set(sys.modules))

def _reload(module=None):
    if module is not None:
        if module not in _modules and sys.modules.get(module) is not None:
            del sys.modules[module]
    _callbacks[state.curdoc].stop()
    state.location.reload = True

def _check_file(modify_times, path, module=None):
    try:
        modified = os.stat(path).st_mtime
    except Exception:
        return
    if path not in modify_times:
        modify_times[path] = modified
        return
    if modify_times[path] != modified:
        _reload(module)
        modify_times[path] = modified

def _reload_on_update(modify_times):
    for mname, module in list(sys.modules.items()):
        # Some modules play games with sys.modules (e.g. email/__init__.py
        # in the standard library), and occasionally this can cause strange
        # failures in getattr.  Just ignore anything that's not an ordinary
        # module.
        if not isinstance(module, types.ModuleType) or mname in _modules:
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        if path.endswith(".pyc") or path.endswith(".pyo"):
            path = path[:-1]
        _check_file(modify_times, path, mname)
    for path in _watched_files:
        _check_file(modify_times, path)
