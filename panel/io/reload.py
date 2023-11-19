import fnmatch
import os
import sys
import types

from contextlib import contextmanager

from watchfiles import awatch

from ..util import fullpath
from .state import state

_watched_files = set()
_modules = set()

# List of paths to ignore
DEFAULT_FOLDER_DENYLIST = [
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


def in_denylist(filepath):
    return any(
        file_is_in_folder_glob(filepath, denylisted_folder)
        for denylisted_folder in DEFAULT_FOLDER_DENYLIST
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

async def async_file_watcher():
    files = list(_watched_files)
    modules = {}
    for module_name in _modules:
        # Some modules play games with sys.modules (e.g. email/__init__.py
        # in the standard library), and occasionally this can cause strange
        # failures in getattr.  Just ignore anything that's not an ordinary
        # module.
        if module_name not in sys.modules:
            continue
        module = sys.modules[module_name]
        if not isinstance(module, types.ModuleType):
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        if path.endswith(".pyc") or path.endswith(".pyo"):
            path = path[:-1]
        modules[path] = module_name
        files.append(path)
    async for changes in awatch(*files):
        for _, path in changes:
            if path in modules:
                if module in sys.modules:
                    del sys.modules[modules[path]]
        _reload()

def autoreload_watcher():
    """
    Installs a periodic callback which checks for changes in watched
    files and sys.modules.
    """
    if not state.curdoc or not state.curdoc.session_context.server_context:
        return
    state.execute(async_file_watcher)

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

            if filepath is None or in_denylist(filepath):
                continue

            if not os.path.isfile(filepath): # e.g. built-in
                continue
            _modules.add(module_name)
        except Exception:
            continue

def _reload():
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
