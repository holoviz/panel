import asyncio
import fnmatch
import logging
import os
import pathlib
import sys
import types
import warnings

from contextlib import contextmanager

from bokeh.application.handlers import CodeHandler

try:
    from watchfiles import awatch
except Exception:
    async def awatch(*files, stop_event=None):
        modify_times = {}
        stop_event = stop_event if stop_event else asyncio.Event()
        while not stop_event.is_set():
            changes = set()
            for path in files:
                change = _check_file(path, modify_times)
                if change:
                    changes.add((change, path))
            if changes:
                yield changes
            await asyncio.sleep(0.5)

from ..util import fullpath
from .state import state

_reload_logger = logging.getLogger('panel.io.reload')

_watched_files = set()
_modules = set()
_local_modules = set()

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
    'panel.',
    'torch.'
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

def watched_modules():
    files = list(_watched_files)
    module_paths = {}
    for module_name in (_modules | _local_modules):
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
        if path.endswith((".pyc", ".pyo")):
            path = path[:-1]
        path = str(pathlib.Path(path).resolve())
        module_paths[path] = module_name
        files.append(path)
    return module_paths, files

async def async_file_watcher(stop_event=None):
    while True:
        module_paths, files = watched_modules()
        async for changes in awatch(*files, stop_event=stop_event):
            _reload(module_paths, changes)
            await asyncio.sleep(1)
            break
        if stop_event.is_set():
            break

async def setup_autoreload_watcher(stop_event=None):
    """
    Installs a periodic callback which checks for changes in watched
    files and sys.modules.
    """
    try:
        import watchfiles  # noqa
    except Exception:
        warnings.warn(
            '--autoreload functionality now depends on the watchfiles '
            'library. In future versions autoreload will not work without '
            'watchfiles being installed. Since it provides a much better '
            'user experience consider installing it today.', FutureWarning,
            stacklevel=0
        )
    _reload_logger.debug('Setting up global autoreload watcher.')
    await async_file_watcher(stop_event=stop_event)

def watch(filename):
    """
    Add a file to the watch list.

    All imported modules are watched by default.
    """
    _watched_files.add(filename)

def is_subpath(subpath, path):
    try:
        return bool(pathlib.Path(subpath).relative_to(pathlib.Path(path)))
    except Exception:
        return False

@contextmanager
def record_modules(applications=None, handler=None):
    """
    Records modules which are currently imported.
    """
    app_paths = set()
    if hasattr(handler, '_runner'):
        app_paths.add(pathlib.Path(handler._runner.path).parent)
    for app in (applications or ()):
        if not app._handlers:
            continue
        for handler in app._handlers:
            if isinstance(handler, CodeHandler):
                break
        else:
            continue
        if hasattr(handler, '_runner'):
            app_paths.add(pathlib.Path(handler._runner.path).parent)
    modules = set(sys.modules)
    yield
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

            parent_path = pathlib.Path(filepath).parent
            if any(parent_path == app_path or is_subpath(app_path, parent_path) for app_path in app_paths):
                _local_modules.add(module_name)
            else:
                _modules.add(module_name)
        except Exception:
            continue

def _reload(module_paths, changes):
    """
    Reloads modules depending on the module files that were changed.
    Specifically we make a distinction between local modules relative
    to the current application paths and global modules. This allows
    us to reload the application itself, any local modules imported
    by the application or all global modules independently.
    """
    _reload_logger.debug('Changes detected by autoreload watcher, unloading modules and reloading sessions.')

    local_, global_ = False, False
    for _, path in changes:
        if path not in module_paths:
            continue
        module = module_paths[path]
        if module in _local_modules and not any(m_.startswith(f'{module}.') for m_ in _modules):
            local_ = True
        else:
            global_ = True

    modules_to_reload = set()
    if global_:
        modules_to_reload |= _modules
    if global_ or local_:
        modules_to_reload |= _local_modules

    for module in modules_to_reload:
        if module in sys.modules:
            del sys.modules[module]

    for doc, loc in state._locations.items():
        if not doc.session_context:
            continue
        elif state._loaded.get(doc):
            loc.reload = True
        else:
            def reload_session(event, loc=loc):
                loc.reload = True
            doc.on_event('document_ready', reload_session)

def _check_file(path, modify_times):
    """
    Checks if a file was modified or deleted and then returns a code,
    modeled after watchfiles, indicating the type of change:

    - 0: No change
    - 2: File modified
    - 3: File deleted

    Arguments
    ---------
    path: str | os.PathLike
      Path of the file to check for modification
    modify_times: dict[str, int]
      Dictionary of modification times for different paths.

    Returns
    -------
    Status code indicating type of change.
    """
    last_modified = modify_times.get(path)
    try:
        modified = os.stat(path).st_mtime
    except FileNotFoundError:
        if last_modified:
            return 3
    except Exception:
        return 0
    if last_modified is None:
        modify_times[path] = modified
        return 0
    elif last_modified != modified:
        modify_times[path] = modified
        return 2
