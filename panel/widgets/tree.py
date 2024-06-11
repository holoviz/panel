"""
Defines various Select widgets which allow choosing one or more items
from a list of options.
"""
from __future__ import annotations

import logging

from abc import abstractmethod
from typing import (
    TYPE_CHECKING, Any, ClassVar, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
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
        jsn = dict(id=id_, text=label, children=children or [], **kwargs)
        if parent:
            jsn["parent"] = parent
        if icon:
            jsn["icon"] = icon
        else:
            jsn["icon"] = "jstree-leaf"
        return jsn

    @classmethod
    def _traverse(cls, node) -> list:
        nodes = [node]
        for subnode in node.get('children', []):
            nodes += cls._traverse(subnode)
        return nodes

    def _reindex(self):
        self._index = {}
        for node in self._nodes:
            for subnode in self._traverse(node):
                self._index[subnode['id']] = subnode

    def _get_properties(self, doc: Document) -> dict[str, Any]:
        props = super()._get_properties(doc)
        if hasattr(self, '_nodes'):  # TODO: This feels wrong...
            props['nodes'] = self._nodes
        return props

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
            children, _ = self._get_children(
                node["text"],
                node["id"],
                **{"children_to_skip": nodes_already_sent, **kwargs}
            )
            parent = self._index[node['id']]
            if 'children' not in parent:
                parent['children'] = []
            for child in children:
                if child['id'] in self._index:
                    continue
                new_nodes.extend(children)
                self._index[child['id']] = child
                parent['children'].append(child)
        self._new_nodes = new_nodes

    @abstractmethod
    def _get_children(self, node_name, node_id, **kwargs):
        """
        Returns the list of children of a node and any children that
        were removed from the node.
        """
        raise NotImplementedError()


class Tree(_TreeBase):
    """

    """

    child_callback = param.Callable(doc="""
        Function used to return the list of children.  Given the node
        name and unique node id the function should return a list of
        jsTree node definitions.""")

    _rename = {**_TreeBase._rename, "child_callback": None}

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
