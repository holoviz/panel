# panel.io.reload module

panel.io.reload.file_is_in_folder_glob(filepath, folderpath_glob)
Test whether a file is in some folder with globbing support.

Parameters:
filepath : str
A file path.

**folderpath_glob: str**
A path to a folder that may include globbing.

panel.io.reload.record_modules(applications=None, handler=None)
Records modules which are currently imported.

async panel.io.reload.setup_autoreload_watcher(stop_event=None)
Installs a periodic callback which checks for changes in watched files
and sys.modules.

panel.io.reload.watch(filename)
Add a file to the watch list.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
