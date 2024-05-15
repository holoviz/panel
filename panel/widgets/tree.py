"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import annotations

import copy
import logging
import os

from abc import abstractmethod
from pathlib import Path, PosixPath
from typing import (
    TYPE_CHECKING, Any, AnyStr, ClassVar, Mapping, Optional,
)
from urllib.parse import urljoin, urlparse

import param

from pyviz_comms import JupyterComm

from ..util import fullpath, lazy_load
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
        Whether to to use checkboxes as selectables""")

    select_multiple = param.Boolean(default=True, doc="""
        Whether multiple nodes can be selected or not""")

    plugins = param.List(doc="""
        Configure which additional plugins will be active.  Should be
        an array of strings, where each element is a plugin name that
        are passed to jsTree.""")

    show_icons = param.Boolean(default=True, doc="Whether to use icons or not")

    show_dots = param.Boolean(default=True, doc="""
        Whether to show dots on the left as part of the tree""")

    value = param.List(default=[], doc="""
        List of currently selected leaves and nodes""")

    _get_parents_cb = param.Callable(doc="""
        Function that is called on a value to load all the parents""")

    # Add a cb for getting parents (fileselector: map(str, Path(value).parents))

    _new_nodes = param.List(doc="Children to push to tree")

    _rename: ClassVar[Mapping[str, str | None]] = {
        "select_multiple": "multiple",
        "_get_parents_cb": None,
        "name": None,
    }

    @property
    def _flat_tree(self):
        return self._flat_tree

    @property  # TODO this is only need in File tree b/c it does special value processing
    def _values(self):
        return self.value

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
        properties["value"] = self._values
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

    def _add_children_on_new_values(self, *event):
        def transverse(d: list, value):
            parents = self._get_parents_cb(value)
            for node in d:
                if node["id"] == value:
                    break
                if node["id"] in parents:
                    node.setdefault("state", {})["opened"] = True
                    if node.get("children"):
                        transverse(node["children"], value)
                    else:
                        node["children"] = self._get_children(
                            node["text"], node["id"], depth=2
                        )
                        for n in node["children"]:
                            if n["id"] in parents:
                                transverse([n], value)
                    break

        ids = [node["id"] for node in self._flat_tree]
        values = [value for value in self._values if value not in ids]
        if values:
            data = copy.deepcopy(self._data[:])
            for value in values:
                transverse(data, value)
            self._data = data

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
    def normalize(path):
        return path


class LocalFileProvider(BaseFileProvider):

    join = os.path.join

    def ls(self, path, file_pattern: str = "[!.]*"):
        if not os.path.isdir(path):
            return [], []
        return _scan_path(path, file_pattern=file_pattern)

    @staticmethod
    def normalize(path, root):
        path = os.path.expanduser(os.path.normpath(path))
        path = Path(path)
        if not path.is_absolute():
            path = Path(root).parent / path
        return str(path)


class RemoteFileProvider(BaseFileProvider):

    join = urljoin

    def __init__(self, fs: AbstractFileSystem):
        self.fs = fs

    @staticmethod
    def join(a, *p) -> str:
        parsed = urlparse(a)
        path = PosixPath('/')
        for sp in p:
            if urlparse(sp).scheme:
                path = sp
            else:
                path /= sp
        if parsed.scheme and not urlparse(str(path)).scheme:
            return f"{parsed.scheme}:/{path}"
        return str(path)

    def ls(self, path: str, file_pattern: str = "[!.]*"):
        if not path.endswith('/'):
            path += '/'
        raw_ls = self.fs.ls(path, detail=True)
        dirs = [d['name'].replace(path, "") for d in raw_ls if d['type'] == 'directory' ]
        raw_glob = self.fs.glob(path+file_pattern, detail=True)
        files = [d['name'].replace(path, "") for d in raw_glob.values() if d['type'] == 'file' ]
        return dirs, files


class FileTree(_TreeBase):
    """
    FileTree renders a path or directory.
    """

    directory = param.String(default=str(Path.cwd()), doc="""
        The directory to explore.""")

    provider = param.ClassSelector(class_=BaseFileProvider, default=LocalFileProvider(), doc="""
        A FileProvider.""")

    _rename = {'directory': None, 'provider': None}

    def __init__(self, directory: AnyStr | os.PathLike | None = None, **params):
        if directory is not None:
            params["directory"] = fullpath(directory)
        self._file_icon = "jstree-file"
        self._folder_icon = "jstree-folder"
        super().__init__(
            _get_parents_cb=lambda value: list(map(str, Path(value).parents)),
            **params
        )

    @property
    def _values(self):
        return [self.provider.normalize(p, self.directory) for p in self.value]

    @param.depends('directory', watch=True, on_init=True)
    def _set_data_from_directory(self, *event):
        self._nodes = [{
            "id": fullpath(self.directory),
            "text": Path(self.directory).name,
            "icon": self._folder_icon,
            "state": {"opened": True},
            "children": self._get_children(Path(self.directory).name, self.directory, depth=1)
        }]

    def _get_properties(self, doc: Document) -> dict[str, Any]:
        props = super()._get_properties(doc)
        props['nodes'] = self._nodes
        return props

    def _get_children(
        self, text: str, directory: str, depth=0, children_to_skip=(), **kwargs
    ):
        parent = str(directory)
        path = self.provider.join(str(self.directory), directory)
        nodes = []
        dirs, files = self._get_paths(path, children_to_skip=children_to_skip)
        for subdir in dirs:
            if depth > 0:
                children = self._get_children(Path(subdir).name, subdir, depth=depth - 1)
            else:
                children = None
            dir_spec = self._to_json(
                id_=subdir, label=Path(subdir).name, parent=parent,
                children=children, icon=self._folder_icon, **kwargs
            )
            nodes.append(dir_spec)
        nodes.extend(
            self._to_json(
                id_=subfile, label=Path(subfile).name, parent=parent,
                icon=self._file_icon, **kwargs
            )
            for subfile in files
        )
        return nodes

    def _get_paths(self, directory, children_to_skip=()):
        dirs_, files = self.provider.ls(directory)
        dirs = []
        for d in dirs_:
            if Path(d).name.startswith(".") or d in children_to_skip:
                continue
            dirs.append(d)
        files = [f for f in files if f not in children_to_skip]
        return sorted(dirs), sorted(files)
