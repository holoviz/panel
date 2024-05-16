"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import annotations

import logging
import os

from abc import abstractmethod
from pathlib import Path
from typing import (
    TYPE_CHECKING, Any, AnyStr, ClassVar, Mapping, Optional,
)
from urllib.parse import urlparse

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import Widget
from .file_selector import _scan_path

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from fsspec import AbstractFileSystem
    from pyviz_comms import Comm

    from ..models.jstree import NodeEvent

logger = logging.getLogger(__file__)


class _TreeBase(Widget):
    """
    jsTree widget allow editing a tree in an jsTree editor.
    """

    checkbox = param.Boolean(default=True, doc="""
        Whether to use checkboxes as selectables""")

    icon_size = param.Integer(default=48)

    select_multiple = param.Boolean(default=True, doc="""
        Whether multiple nodes can be selected or not""")

    plugins = param.List(doc="""
        Configure which additional plugins will be active.  Should be
        an array of strings, where each element is a plugin name that
        are passed to jsTree.""")

    sort = param.Boolean(default=False, doc="""
        Whether to sort nodes alphabetically.""")

    show_icons = param.Boolean(default=True, doc="Whether to use icons or not.")

    show_dots = param.Boolean(default=False, doc="""
        Whether to show dots on the left as part of the tree.""")

    show_stripes = param.Boolean(default=False, doc="""
        Whether to show stripes on alternating rows.""")

    value = param.List(default=[], doc="""
        List of currently selected leaves and nodes""")

    _new_nodes = param.List(default=None, doc="Children to push to tree")

    _rename: ClassVar[Mapping[str, str | None]] = {
        "icon_size": None,
        "select_multiple": "multiple",
        "name": None,
    }

    @staticmethod
    def _to_json(
        id_, label, parent: str = None, children: Optional[list] = None,
        icon: str = None, **kwargs
    ):
        jsn = dict(id=id_, text=label, **kwargs)
        if parent:
            jsn["parent"] = parent
        if children:
            jsn["children"] = children
        if icon:
            jsn["icon"] = icon
        else:
            jsn["icon"] = "jstree-leaf"
        return jsn

    def _process_param_change(self, msg: dict[str, Any]) -> dict[str, Any]:
        properties = super()._process_param_change(msg)
        if properties.get("height") and properties["height"] < 100:
            properties["height"] = 100
        if 'icon_size' in properties or 'stylesheets' in properties:
            properties['stylesheets'] = [
                f':host {{ --icon-size: {self.icon_size}px; }}'
            ] + properties.get('stylesheets', self.stylesheets)
        properties["value"] = self.value
        return properties

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.jstree', 'jsTree', isinstance(comm, JupyterComm),
                root, ext='tree'
            )
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('node_event', model=model, doc=doc, comm=comm)
        return model

    def _process_event(self, event: NodeEvent):
        if event.data['type'] == 'open':
            self._add_children_on_node_open(event)

    def _add_children_on_node_open(self, event: NodeEvent, **kwargs):
        opened_node = event.data["node"]
        nodes_already_sent = opened_node.get("children_d", [])
        children_nodes = opened_node["children_nodes"]
        new_nodes = []
        for node in children_nodes:
            children = self._get_children(
                node["text"],
                node["id"],
                **{"children_to_skip": nodes_already_sent, **kwargs}
            )
            if children:
                new_nodes.extend(children)
        self._new_nodes = new_nodes

    @abstractmethod
    def _get_children(self, node_name, node_id, **kwargs):
        raise NotImplementedError()



class Tree(_TreeBase):
    """

    """

    child_callback = param.Callable(doc="""
        Function used to return the list of children.  Given the node
        name and unique node id the function should return a list of
        jsTree node definitions.""")

    def _get_children(self, node_name, node_id, **kwargs) -> list[dict[str, any]]:
        if self.child_callback:
            return self.child_callback(node_name, node_id, **kwargs)
        return []

    @property
    def data(self):
        """When swapping out data, you are not able to input selections data on nodes.
        All nodes will start out deselected.
        """
        return self._data

    @data.setter
    def data(self, value):
        self._data = value


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


class FileTree(_TreeBase):
    """
    FileTree renders a path or directory.
    """

    paths = param.List(default=[Path.cwd()], doc="""
        The directory paths to explore.""")

    provider = param.ClassSelector(class_=BaseFileProvider, default=LocalFileProvider(), doc="""
        A FileProvider.""")

    sort = param.Boolean(default=True, doc="""
        Whether to sort nodes alphabetically.""")

    _rename = {'paths': None, 'provider': None}

    def __init__(self, paths: list[AnyStr | os.PathLike] | AnyStr | os.PathLike | None = None, **params):
        provider = params.get('provider', self.provider)
        if isinstance(paths, list):
            paths = [provider.normalize(p) for p in paths]
        elif paths is not None:
            paths = [provider.normalize(paths)]
        else:
            paths = []
        super().__init__(paths=paths, **params)

    @param.depends('paths', watch=True, on_init=True)
    def _set_data_from_directory(self, *event):
        self._nodes = [{
            "id": self.provider.normalize(path),
            "text": Path(path).name,
            "icon": "jstree-folder",
            "type": "folder",
            "state": {"opened": True},
            "children": self._get_children(Path(path).name, path, depth=1)
        } for path in self.paths]

    def _get_properties(self, doc: Document) -> dict[str, Any]:
        props = super()._get_properties(doc)
        props['nodes'] = self._nodes
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
