import fnmatch
import os
import sys
import types

from contextlib import contextmanager
from functools import partial

from ..util import fullpath
from .callbacks import PeriodicCallback
from .state import state

_watched_files = set()
_modules = set()
_callbacks = {}

# List of paths to ignore
DEFAULT_FOLDER_BLACKLIST = [
    "**/.*",
    "**/anaconda",
    "**/anaconda2",
    "**/anaconda3",
    "**/dist-packages",
    "**/miniconda",
    "**/miniconda2",
    "**/miniconda3",
    "**/node_modules",
    "**/pyenv",
    "**/site-packages",
    "**/venv",
    "**/virtualenv",
]

IGNORED_MODULES = [
    'bokeh_app',
    'panel.'
]


def in_blacklist(filepath):
    return any(
        file_is_in_folder_glob(filepath, blacklisted_folder)
        for blacklisted_folder in DEFAULT_FOLDER_BLACKLIST
    )

def file_is_in_folder_glob(filepath, folderpath_glob):
    """
    Test whether a file is in some folder with globbing support.

    Parameters
    ----------
    filepath : str
        A file path.
    folderpath_glob: str
        A path to a folder that may include globbing.
    """
    # Make the glob always end with "/*" so we match files inside subfolders of
    # folderpath_glob.
    if not folderpath_glob.endswith("*"):
        if folderpath_glob.endswith("/"):
            folderpath_glob += "*"
        else:
            folderpath_glob += "/*"

    file_dir = os.path.dirname(filepath) + "/"
    return fnmatch.fnmatch(file_dir, folderpath_glob)

def autoreload_watcher():
    """
    Installs a periodic callback which checks for changes in watched
    files and sys.modules.
    """
    cb = partial(_reload_on_update, {})
    _callbacks[state.curdoc] = pcb = PeriodicCallback(callback=cb, background=True)
    pcb.start()

def watch(filename):
    """
    Add a file to the watch list.

    All imported modules are watched by default.
    """
    _watched_files.add(filename)

@contextmanager
def record_modules():
    """
    Records modules which are currently imported.
    """
    modules = set(sys.modules)
    yield
    if _modules:
        return
    for module_name in set(sys.modules).difference(modules):
        if any(module_name.startswith(imodule) for imodule in IGNORED_MODULES):
            continue
        module = sys.modules[module_name]
        try:
            spec = getattr(module, "__spec__", None)
            if spec is None:
                filepath = getattr(module, "__file__", None)
                if filepath is None: # no user
                    continue
            else:
                filepath = spec.origin

            filepath = fullpath(filepath)

            if filepath is None or in_blacklist(filepath):
                continue

            if not os.path.isfile(filepath): # e.g. built-in
                continue
            _modules.add(module_name)
        except Exception:
            continue

def _reload(module=None):
    if module is not None:
        for module in _modules:
            if module in sys.modules:
                del sys.modules[module]
    for cb in _callbacks.values():
        cb.stop()
    _callbacks.clear()
    if state.location is not None:
        # In case session has been cleaned up
        state.location.reload = True
    for loc in state._locations.values():
        loc.reload = True

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
    for module_name in _modules:
        # Some modules play games with sys.modules (e.g. email/__init__.py
        # in the standard library), and occasionally this can cause strange
        # failures in getattr.  Just ignore anything that's not an ordinary
        # module.
        if not module_name in sys.modules:
            continue
        module = sys.modules[module_name]
        if not isinstance(module, types.ModuleType):
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        if path.endswith(".pyc") or path.endswith(".pyo"):
            path = path[:-1]
        _check_file(modify_times, path, module_name)
    for path in _watched_files:
        _check_file(modify_times, path)
