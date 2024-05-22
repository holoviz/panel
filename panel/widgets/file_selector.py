"""
Defines a FileSelector widget which allows selecting files and
directories on the server.
"""
from __future__ import annotations

import os

from abc import abstractmethod
from fnmatch import fnmatch
from pathlib import Path
from typing import (
    TYPE_CHECKING, AnyStr, ClassVar, Optional,
)
from urllib.parse import urlparse

import param

from ..io import PeriodicCallback
from ..layout import (
    Column, Divider, ListPanel, Row,
)
from ..models.widgets import DoubleClickEvent
from ..util import fullpath
from ..viewable import Layoutable
from .base import CompositeWidget
from .button import Button
from .input import TextInput
from .select import CrossSelector
from .tree import _TreeBase

if TYPE_CHECKING:
    from fsspec import AbstractFileSystem


def _scan_path(path: str, file_pattern='*') -> tuple[list[str], list[str]]:
    """
    Scans the supplied path for files and directories and optionally
    filters the files with the file keyword, returning a list of sorted
    paths of all directories and files.

    Arguments
    ---------
    path: str
        The path to search
    file_pattern: str
        A glob-like pattern to filter the files

    Returns
    -------
    A sorted list of directory paths, A sorted list of files
    """
    paths = [os.path.join(path, p) for p in os.listdir(path)]
    dirs = [p for p in paths if os.path.isdir(p)]
    files = [p for p in paths if os.path.isfile(p) and
             fnmatch(os.path.basename(p), file_pattern)]
    for p in paths:
        if not os.path.islink(p):
            continue
        path = os.path.realpath(p)
        if os.path.isdir(path):
            dirs.append(p)
        elif os.path.isfile(path):
            dirs.append(p)
        else:
            continue
    return dirs, files


class BaseFileProvider:

    @abstractmethod
    def ls(self, path):
        """
        Concrete classes must implement this method to list the content of a remote filesystem.

        Arguments
        ---------
        path: str
            The path to search

        Returns
        -------
        A tuple of two lists: the first one contains the directories, the second one contains the files.
        Each element of the lists is a string representing the *name* (not the full path) of the directory or file.
        """
        raise NotImplementedError()

    @staticmethod
    def normalize(path, root=None):
        return path


class LocalFileProvider(BaseFileProvider):

    def ls(self, path, file_pattern: str = "[!.]*"):
        if not os.path.isdir(path):
            return [], []
        return _scan_path(path, file_pattern=file_pattern)

    def isdir(self, path):
        return os.path.isdir(path)

    @staticmethod
    def normalize(path, root=None):
        path = os.path.expanduser(os.path.normpath(path))
        path = Path(path)
        if not path.is_absolute():
            if root:
                path = Path(root).parent / path
            else:
                path = path.resolve()
        return str(path)


class RemoteFileProvider(BaseFileProvider):

    def __init__(self, fs: AbstractFileSystem):
        self.fs = fs

    def isdir(self, path):
        return self.fs.isdir(path)

    def ls(self, path: str, file_pattern: str = "[!.]*"):
        if not path.endswith('/'):
            path += '/'
        raw_ls = self.fs.ls(path, detail=True)
        prefix = ''
        if scheme:= urlparse(path).scheme:
            prefix = f'{scheme}://'
        dirs = [f"{prefix}{d['name']}/" for d in raw_ls if d['type'] == 'directory' ]
        raw_glob = self.fs.glob(path+file_pattern, detail=True)
        files = [f"{prefix}{d['name']}" for d in raw_glob.values() if d['type'] == 'file' ]
        return dirs, files


class BaseFileSelector(param.Parameterized):

    directory = param.String(default=os.getcwd(), doc="""
        The directory to explore.""")

    file_pattern = param.String(default='*', doc="""
        A glob-like pattern to filter the files.""")

    only_files = param.Boolean(default=False, doc="""
        Whether to only allow selecting files.""")

    root_directory = param.String(default=None, doc="""
        If set, overrides directory parameter as the root directory
        beyond which users cannot navigate.""")

    provider = param.ClassSelector(class_=BaseFileProvider, default=LocalFileProvider(), doc="""
        A FileProvider that allows explore local and remote file systems.""")

    value = param.List(default=[], doc="""
        List of selected files.""")

    def __init__(self, directory: AnyStr | os.PathLike | None = None, **params):
        provider = params.get('provider', self.provider)
        if directory is not None:
            params["directory"] = provider.normalize(directory)
        if 'root_directory' in params:
            root = params['root_directory']
            params['root_directory'] = provider.normalize(root)
        super().__init__(**params)


class FileSelector(BaseFileSelector, CompositeWidget):
    """
    The `FileSelector` widget allows browsing the filesystem on the
    server and selecting one or more files in a directory.

    Reference: https://panel.holoviz.org/reference/widgets/FileSelector.html

    :Example:

    >>> FileSelector(directory='~', file_pattern='*.png')
    """

    show_hidden = param.Boolean(default=False, doc="""
        Whether to show hidden files and directories (starting with
        a period).""")

    size = param.Integer(default=10, doc="""
        The number of options shown at once (note this is the only
        way to control the height of this widget)""")

    refresh_period = param.Integer(default=None, doc="""
        If set to non-None value indicates how frequently to refresh
        the directory contents in milliseconds.""")

    _composite_type: ClassVar[type[ListPanel]] = Column

    def __init__(self, directory: AnyStr | os.PathLike | None = None, **params):
        from ..pane import Markdown
        if params.get('width') and params.get('height') and 'sizing_mode' not in params:
            params['sizing_mode'] = None
        super().__init__(directory=directory, **params)

        # Set up layout
        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height', 'margin') and getattr(self, p) is not None}
        sel_layout = dict(layout, sizing_mode='stretch_width', height=300, margin=0)
        self._selector = CrossSelector(
            filter_fn=lambda p, f: fnmatch(f, p), size=self.size, **sel_layout
        )

        self._back = Button(name='◀', width=40, height=40, margin=(5, 10, 0, 0), disabled=True, align='center')
        self._forward = Button(name='▶', width=40, height=40, margin=(5, 10, 0, 0), disabled=True, align='center')
        self._up = Button(name='⬆', width=40, height=40, margin=(5, 10, 0, 0), disabled=True, align='center')
        self._directory = TextInput(value=self.directory, margin=(5, 10, 0, 0), width_policy='max', height_policy='max')
        self._go = Button(name='⬇', disabled=True, width=40, height=40, margin=(5, 5, 0, 0), align='center')
        self._reload = Button(name='↻', width=40, height=40, margin=(5, 0, 0, 10), align='center')
        self._nav_bar = Row(
            self._back, self._forward, self._up, self._directory, self._go, self._reload,
            **dict(layout, width=None, margin=0, width_policy='max')
        )
        self._composite[:] = [self._nav_bar, Divider(margin=0), self._selector]
        style = 'h4 { margin-block-start: 0; margin-block-end: 0;}'
        self._selector._selected.insert(0, Markdown('#### Selected files', margin=0, stylesheets=[style]))
        self._selector._unselected.insert(0, Markdown('#### File Browser', margin=0, stylesheets=[style]))
        self.link(self._selector, size='size')

        # Set up state
        self._stack = []
        self._cwd = None
        self._position = -1
        self._update_files(True)

        # Set up callback
        self._selector._lists[False].on_double_click(self._select_and_go)
        self.link(self._directory, directory='value')
        self._selector.param.watch(self._update_value, 'value')
        self._go.on_click(self._update_files)
        self._reload.on_click(self._update_files)
        self._up.on_click(self._go_up)
        self._back.on_click(self._go_back)
        self._forward.on_click(self._go_forward)
        self._directory.param.watch(self._dir_change, 'value')
        self._selector._lists[False].param.watch(self._select, 'value')
        self._selector._lists[False].param.watch(self._filter_denylist, 'options')
        self._periodic = PeriodicCallback(callback=self._refresh, period=self.refresh_period or 0)
        self.param.watch(self._update_periodic, 'refresh_period')
        if self.refresh_period:
            self._periodic.start()

    def _select_and_go(self, event: DoubleClickEvent):
        relpath = event.option.replace('📁', '').replace('⬆ ', '')
        if relpath == '..':
            return self._go_up()
        sel = fullpath(os.path.join(self._cwd, relpath))
        if self.provider.isdir(sel):
            self._directory.value = sel
        else:
            self._directory.value = self._cwd
        self._update_files()

    def _update_periodic(self, event: param.parameterized.Event):
        if event.new:
            self._periodic.period = event.new
            if not self._periodic.running:
                self._periodic.start()
        elif self._periodic.running:
            self._periodic.stop()

    @property
    def _root_directory(self):
        return self.root_directory or self.directory

    def _update_value(self, event: param.parameterized.Event):
        value = [v for v in event.new if v != '..' and (not self.only_files or os.path.isfile(v))]
        self._selector.value = value
        self.value = value

    def _dir_change(self, event: param.parameterized.Event):
        path = fullpath(self._directory.value)
        if not path.startswith(self._root_directory):
            self._directory.value = self._root_directory
            return
        elif path != self._directory.value:
            self._directory.value = path
        self._go.disabled = path == self._cwd

    def _refresh(self):
        self._update_files(refresh=True)

    def _update_files(
        self, event: Optional[param.parameterized.Event] = None, refresh: bool = False
    ):
        path = self.provider.normalize(self._directory.value)
        refresh = refresh or (event and getattr(event, 'obj', None) is self._reload)
        if refresh:
            path = self._cwd
        elif not self.provider.isdir(path):
            self._selector.options = ['Entered path is not valid']
            self._selector.disabled = True
            return
        elif event is not None and (not self._stack or path != self._stack[-1]):
            self._stack.append(path)
            self._position += 1

        self._cwd = path
        if not refresh:
            self._go.disabled = True
        self._up.disabled = path == self._root_directory
        if self._position == len(self._stack)-1:
            self._forward.disabled = True
        if 0 <= self._position and len(self._stack) > 1:
            self._back.disabled = False

        selected = self.value
        dirs, files = self.provider.ls(path, self.file_pattern)
        for s in selected:
            check = os.path.realpath(s) if os.path.islink(s) else s
            if os.path.isdir(check):
                dirs.append(s)
            elif os.path.isfile(check):
                files.append(s)

        paths = [
            p for p in sorted(dirs)+sorted(files)
            if self.show_hidden or not os.path.basename(p).startswith('.')
        ]
        abbreviated = [
            ('📁' if f in dirs else '')+os.path.relpath(f, self._cwd)
            for f in paths
        ]
        if not self._up.disabled:
            paths.insert(0, '..')
            abbreviated.insert(0, '⬆ ..')

        options = dict(zip(abbreviated, paths))
        self._selector.options = options
        self._selector.value = selected

    def _filter_denylist(self, event: param.parameterized.Event):
        """
        Ensure that if unselecting a currently selected path and it
        is not in the current working directory then it is removed
        from the denylist.
        """
        dirs, files = self.provider.ls(self._cwd, self.file_pattern)
        paths = [('📁' if p in dirs else '')+os.path.relpath(p, self._cwd) for p in dirs+files]
        denylist = self._selector._lists[False]
        options = dict(self._selector._items)
        self._selector.options.clear()
        prefix = [] if self._up.disabled else [('⬆ ..', '..')]
        self._selector.options.update(prefix+[
            (k, v) for k, v in options.items() if k in paths or v in self.value
        ])
        options = [o for o in denylist.options if o in paths]
        if not self._up.disabled:
            options.insert(0, '⬆ ..')
        denylist.options = options

    def _select(self, event: param.parameterized.Event):
        if len(event.new) != 1:
            self._directory.value = self._cwd
            return

        relpath = event.new[0].replace('📁', '').replace('⬆ ', '')
        sel = fullpath(os.path.join(self._cwd, relpath))
        if os.path.isdir(sel):
            self._directory.value = sel
        else:
            self._directory.value = self._cwd

    def _go_back(self, event: param.parameterized.Event):
        self._position -= 1
        self._directory.value = self._stack[self._position]
        self._update_files()
        self._forward.disabled = False
        if self._position == 0:
            self._back.disabled = True

    def _go_forward(self, event: param.parameterized.Event):
        self._position += 1
        self._directory.value = self._stack[self._position]
        self._update_files()

    def _go_up(self, event: Optional[param.parameterized.Event] = None):
        path = self._cwd.split(os.path.sep)
        self._directory.value = os.path.sep.join(path[:-1]) or os.path.sep
        self._update_files(True)


class FileTree(BaseFileSelector, _TreeBase):
    """
    FileTree renders a path or directory.
    """

    sort = param.Boolean(default=True, doc="""
        Whether to sort nodes alphabetically.""")

    _rename = {
        'directory': None,
        'file_pattern': None,
        'root_directory': None,
        'provider': None,
        'only_files': 'cascade',
        **_TreeBase._rename,
    }

    @param.depends('directory', watch=True, on_init=True)
    def _set_data_from_directory(self, *event):
        self._nodes = [{
            "id": self.provider.normalize(self.directory),
            "text": Path(self.directory).name,
            "icon": "jstree-folder",
            "type": "folder",
            "state": {"opened": True},
            "children": self._get_children(Path(self.directory).name, self.directory, depth=1)
        }]
        self._reindex()

    def _process_property_change(self, msg):
        props = super()._process_property_change(msg)
        if 'value' in props and self.only_files:
            props['value'] = [
                node_id for node_id in props['value']
                if self._index.get(node_id, {}).get('type') == 'file'
            ]
        return props

    def _get_children(
        self, text: str, directory: str, depth=0, children_to_skip=(), **kwargs
    ):
        parent = str(directory)
        nodes = []
        dirs, files = self._get_paths(directory, children_to_skip=children_to_skip)
        for subdir in dirs:
            if depth > 0:
                children = self._get_children(Path(subdir).name, subdir, depth=depth - 1)
            else:
                children = None
            dir_spec = self._to_json(
                id_=subdir, label=Path(subdir).name, parent=parent,
                children=children, icon="jstree-folder", type='folder', **kwargs
            )
            nodes.append(dir_spec)
        nodes.extend(
            self._to_json(
                id_=subfile, label=Path(subfile).name, parent=parent,
                icon="jstree-file", type='file', **kwargs
            )
            for subfile in files
        )
        return nodes

    def _get_paths(self, directory, children_to_skip=()):
        dirs_, files = self.provider.ls(str(directory))
        dirs = []
        for d in dirs_:
            if Path(d).name.startswith(".") or d in children_to_skip:
                continue
            dirs.append(d)
        files = [f for f in files if f not in children_to_skip]
        return sorted(dirs), sorted(files)
