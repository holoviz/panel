"""
Defines a FileSelector widget which allows selecting files and
directories on the server.
"""
from __future__ import annotations

import os

from abc import abstractmethod
from fnmatch import fnmatch
from importlib.util import find_spec
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

    fs = None

    @classmethod
    def from_filesystem(cls, fs):
        if fs is None:
            return LocalFileProvider()
        elif find_spec('fsspec'):
            from fsspec import AbstractFileSystem
            if isinstance(fs, AbstractFileSystem):
                return RemoteFileProvider(fs)
        raise ValueError(f"Unsupported filesystem type: {type(fs)}")

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

    sep = os.path.sep

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

    sep = '/'

    def __init__(self, fs: AbstractFileSystem):
        self.fs = fs

    def isdir(self, path):
        return self.fs.isdir(path)

    def ls(self, path: str, file_pattern: str = "[!.]*"):
        if not path.endswith(self.sep):
            path += self.sep
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

    value = param.List(default=[], doc="""
        List of selected files.""")

    def __init__(
        self,
        directory: AnyStr | os.PathLike | None = None,
        fs: AbstractFileSystem | None = None,
        **params,
    ):
        self._provider = BaseFileProvider.from_filesystem(fs)
        if directory is not None:
            params["directory"] = self._provider.normalize(directory)
        if 'root_directory' in params:
            root = params['root_directory']
            params['root_directory'] = self._provider.normalize(root)
        elif directory:
            params['root_directory'] = params['directory']
        super().__init__(**params)

    @property
    def fs(self):
        return self._provider.fs


class BaseFileNavigator(BaseFileSelector, CompositeWidget):

    _composite_type: ClassVar[type[ListPanel]] = Column

    def __init__(self, directory: AnyStr | os.PathLike | None = None, **params):
        super().__init__(directory=directory, **params)

        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height', 'margin') and getattr(self, p) is not None}

        self._back = Button(
            name='◀', width=40, height=40, margin=(5, 10, 0, 0), disabled=True,
            align='end', on_click=self._go_back
        )
        self._forward = Button(
            name='▶', width=40, height=40, margin=(5, 10, 0, 0), disabled=True,
            align='end', on_click=self._go_forward
        )
        self._up = Button(
            name='⬆', width=40, height=40, margin=(5, 10, 0, 0), disabled=True,
            align='end', on_click=self._go_up
        )
        self._directory = TextInput.from_param(
            self.param.directory, margin=(5, 10, 0, 0), width_policy='max', height_policy='max'
        )
        self._go = Button(
            name='⬇', disabled=True, width=40, height=40, margin=(5, 5, 0, 0),
            align='end', on_click=self._update_files
        )
        self._reload = Button(
            name='↻', width=40, height=40, margin=(5, 0, 0, 10), align='end',
            on_click=self._update_files
        )
        self._nav_bar = Row(
            self._back, self._forward, self._up, self._directory, self._go, self._reload,
            **dict(layout, width=None, margin=0, width_policy='max')
        )
        self._composite[:] = [self._nav_bar, Divider(margin=0), self._selector]
        self._directory.param.watch(self._dir_change, 'value')
        self._directory.param.watch(self._update_files, 'enter_pressed')

        # Set up state
        self._stack = []
        self._cwd = None
        self._position = -1
        self._update_files(True)

    @property
    def _root_directory(self):
        return self.root_directory or self.directory

    def _dir_change(self, event: param.parameterized.Event):
        path = fullpath(event.new)
        if not path.startswith(self._root_directory):
            self.directory = fullpath(event.old)
            return
        elif path != self.directory:
            self.directory = path
        self._go.disabled = path == self._cwd

    def _refresh(self):
        self._update_files(refresh=True)

    def _go_back(self, event: param.parameterized.Event):
        self._position -= 1
        self.directory = self._stack[self._position]
        self._update_files()
        self._forward.disabled = False
        if self._position == 0:
            self._back.disabled = True

    def _go_forward(self, event: param.parameterized.Event):
        self._position += 1
        self.directory = self._stack[self._position]
        self._update_files()

    def _go_up(self, event: Optional[param.parameterized.Event] = None):
        path = self._cwd.split(os.path.sep)
        self.directory = os.path.sep.join(path[:-1]) or os.path.sep
        self._update_files(True)

    def _update_files(
        self, event: Optional[param.parameterized.Event] = None, refresh: bool = False
    ):
        path = self._provider.normalize(self._directory.value)
        refresh = refresh or (event and getattr(event, 'obj', None) is self._reload)
        if refresh:
            path = self._cwd
        elif not self._provider.isdir(path):
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


class FileSelector(BaseFileNavigator):
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

    def __init__(
        self,
        directory: AnyStr | os.PathLike | None = None,
        fs: AbstractFileSystem | None = None,
        **params,
    ):
        from ..pane import Markdown
        if params.get('width') and params.get('height') and 'sizing_mode' not in params:
            params['sizing_mode'] = None

        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height', 'margin') and getattr(self, p) is not None}
        sel_layout = dict(layout, sizing_mode='stretch_width', height=300, margin=0)
        self._selector = CrossSelector(
            filter_fn=lambda p, f: fnmatch(f, p), size=self.param.size, **sel_layout
        )

        super().__init__(directory=directory, fs=fs, **params)

        style = 'h4 { margin-block-start: 0; margin-block-end: 0;}'
        self._selector._selected.insert(0, Markdown('#### Selected files', margin=0, stylesheets=[style]))
        self._selector._unselected.insert(0, Markdown('#### File Browser', margin=0, stylesheets=[style]))

        # Set up callback
        self._selector._lists[False].on_double_click(self._select_and_go)
        self._selector.param.watch(self._update_value, 'value')
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
        if self._provider.isdir(sel):
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

    def _update_value(self, event: param.parameterized.Event):
        value = [v for v in event.new if v != '..' and (not self.only_files or os.path.isfile(v))]
        self._selector.value = value
        self.value = value

    def _update_files(
        self, event: Optional[param.parameterized.Event] = None, refresh: bool = False
    ):
        path = self._provider.normalize(self._directory.value)
        super()._update_files(event, refresh)
        selected = self.value
        dirs, files = self._provider.ls(path, self.file_pattern)
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
        dirs, files = self._provider.ls(self._cwd, self.file_pattern)
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


class FileTree(BaseFileSelector, _TreeBase):
    """
    FileTree renders a path or directory.
    """

    sort = param.Boolean(default=True, doc="""
        Whether to sort nodes alphabetically.""")

    max_depth = param.Integer(default=0, doc="""
        The maximum depth to display in the tree.
        If set to 0, all levels are shown.""")

    _rename = {
        'directory': None,
        'file_pattern': None,
        'root_directory': None,
        'only_files': 'cascade',
        'max_depth': None,
        **_TreeBase._rename,
    }

    def __init__(
        self,
        directory: AnyStr | os.PathLike | None = None,
        fs: AbstractFileSystem | None = None,
        **params,
    ):
        self._index = {}
        super().__init__(directory, fs, **params)
        self._internal_callbacks.append(
            self.param.watch(self._set_data_from_directory, 'directory')
        )
        self._set_data_from_directory()

    def _set_data_from_directory(self, event=None):
        try:
            children, _ = self._get_children(
                Path(self.directory).name, self.directory, depth=1
            )
        except FileNotFoundError:
            self.directory = event.old
            return
        node_id = self._provider.normalize(self.directory)+self._provider.sep
        self._nodes = [{
            "id": node_id,
            "text": Path(self.directory).name,
            "icon": "jstree-folder",
            "type": "folder",
            "state": {"opened": True, "loaded": True},
            "children": children
        }]
        self._reindex()
        if event:
            self._param_change(event)

    def _process_param_change(self, params):
        if 'directory' in params:
            params['nodes'] = self._nodes
            del params['directory']
        props = super()._process_param_change(params)
        return props

    def _process_property_change(self, msg):
        props = super()._process_property_change(msg)
        if "value" in props:
            for v in self.value:
                if v in self._index and v not in props['value']:
                    self._index[v]["state"]["selected"] = False
            for v in props["value"]:
                if v in self._index:
                    self._index[v]["state"] = dict(self._index[v].get("state", {}), selected=True)
            if self.only_files:
                props["value"] = [
                    node_id for node_id in props["value"]
                    if self._index.get(node_id, {}).get("type") == "file"
                ]
        return props

    def _exceed_max_depth(self, path):
        if not self.max_depth:
            return False
        current_depth = len(path.relative_to(self.directory).parents)
        return current_depth >= self.max_depth

    def _get_children(self, text: str, directory: str, depth=0, children_to_skip=(), **kwargs):
        if self._exceed_max_depth(Path(directory)):
            return []
        parent = str(directory)  # TODO(hoxbro): Either the type hint is wrong or this is not needed
        nodes = []
        dirs, files = self._get_paths(directory, children_to_skip=children_to_skip)
        parent_node = self._index.get(parent)
        if parent_node:
            removed = [sn for sn in parent_node['children'] if sn['id'] not in dirs+files]
            parent_node['children'] = [sn for sn in parent_node['children'] if sn not in removed]
        else:
            removed = []
        for subdir in dirs:
            subdir_p = Path(subdir)
            load = depth > 0 or self._index.get(subdir, {}).get('state', {}).get("opened")
            if load:
                children, removed_children = self._get_children(
                    subdir_p.name, subdir, depth=depth-1
                )
                removed.extend(removed_children)
            else:
                children, removed_children = [], []
            if subdir in self._index:
                dir_spec = self._index[subdir]
                dir_spec['children'] = children
                dir_spec['state'] = {"loaded": load, "opened": dir_spec.get('state', {}).get("opened", False)}
            else:
                dir_spec = self._to_json(
                    id_=subdir, label=subdir_p.name, parent=parent,
                    children=children, icon="jstree-folder", type='folder',
                    state={"loaded": depth > 0}, **kwargs
                )
            if self._exceed_max_depth(subdir_p):
                dir_spec["state"] = {"disabled": True}
            nodes.append(dir_spec)
        for subfile in files:
            if subfile in self._index:
                file_node = self._index[subfile]
            else:
                file_node = self._to_json(
                    id_=subfile, label=Path(subfile).name, parent=parent,
                    icon="jstree-file", type='file', **kwargs
                )
            nodes.append(file_node)
        return nodes, removed

    def _get_paths(self, directory, children_to_skip=()):
        dirs_, files = self._provider.ls(str(directory))
        dirs = []
        for d in dirs_:
            if Path(d).name.startswith(".") or d in children_to_skip:
                continue
            dirs.append(d)
        files = [f for f in files if f not in children_to_skip]
        return sorted(dirs), sorted(files)


class FileTreeSelector(BaseFileNavigator):
    """
    The `FileTreeSelector` widget allows browsing the filesystem on the
    server and selecting one or more files in a directory using a tree
    based UI.

    Reference: https://panel.holoviz.org/reference/widgets/FileTreeSelector.html

    :Example:

    >>> FileTreeSelector(directory='~', file_pattern='*.png')
    """

    def __init__(
        self,
        directory: AnyStr | os.PathLike | None = None,
        fs: AbstractFileSystem | None = None,
        **params,
    ):
        layout = {p: getattr(self, p) for p in Layoutable.param
                  if p not in ('name', 'height', 'margin') and getattr(self, p) is not None}
        sel_layout = dict(layout, sizing_mode='stretch_width', height=300, margin=0)
        self._selector = FileTree(directory=directory, fs=fs, **sel_layout)
        self._selector.param.watch(self._sync_directory, 'directory')
        super().__init__(directory=directory, fs=fs, **params)

    def _sync_directory(self, event):
        self.directory = event.new

    def _update_files(
        self, event: Optional[param.parameterized.Event] = None, refresh: bool = False
    ):
        self._selector.directory = self._provider.normalize(self._directory.value)
        super()._update_files(event, refresh)
