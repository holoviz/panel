"""
Editable template
"""
from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING

import param

from bokeh.models import CustomJS

from ...config import config
from ...reactive import ReactiveHTML
from ..vanilla import VanillaTemplate

if TYPE_CHECKING:
    from bokeh.document import Document
    from pyviz_comms import Comm

    from ...io.location import Location


class TemplateEditor(ReactiveHTML):
    """
    Component responsible for watching the template for changes and syncing
    the current layout state with Python.
    """

    layout = param.List(doc="""
        The current layout of the template, which is updated by the editor.
        It is a list of dictionaries with the keys 'id', 'width', 'height', and 'visible'.
        The 'id' corresponds to the component's model id, while 'width' and 'height'
        are in percentage of the grid cell size.""")

    _scripts = {
        'render': """
        var grid = window.muuriGrid;
        function save_layout() {
          const layout = [];
          for (const item of grid.getItems()) {
            const el = item.getElement();
            let height = el.style.height.slice(null, -2);
            if (!height) {
              const {top} = item.getMargin();
              height = item.getHeight()-top;
            } else {
              height = parseFloat(height);
            }
            let width;
            if (el.style.width.length) {
              width = parseFloat(el.style.width.split('(')[1].split('%')[0]);
            } else {
              width = 100;
            }
            layout.push({
              id: el.getAttribute('data-id'),
              width: width,
              height: height,
              visible: item.isVisible(),
            })
          }
          data.layout = layout;
        }
        grid.on('layoutEnd', save_layout)
        if (window.resizeableGrid) {
          window.resizeableGrid.on('resizeend', save_layout)
        }
        """
    }


class EditableTemplate(VanillaTemplate):
    """
    The `EditableTemplate` is a list based template with a header, sidebar, main and modal area.
    The template allow interactively dragging, resizing and hiding components on a grid.

    The template builds on top of Muuri and interact.js.

    Reference: https://panel.holoviz.org/reference/templates/EditableTemplate.html

    :Example:

    >>> pn.template.EditableTemplate(
    ...     site="Panel", title="EditableTemplate",
    ...     sidebar=[pn.pane.Markdown("## Settings"), some_slider],
    ...     main=[some_python_object]
    ... ).servable()
    """

    editable = param.Boolean(default=True, doc="""
      Whether the template layout should be editable.""")

    layout = param.Dict(default={}, allow_refs=True, doc="""
      The layout definition of the template indexed by the id of
      each component in the main area.""")

    local_save = param.Boolean(default=True, doc="""
      Whether to enable saving to local storage.""")

    _css = [
        pathlib.Path(__file__).parent.parent / 'vanilla' / "vanilla.css",
        pathlib.Path(__file__).parent / 'editable.css'
    ]

    _resources = {
        "css": {"lato": "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"},
        "js": {
            "interactjs": f"{config.npm_cdn}/interactjs@1.10.19/dist/interact.min.js",
            "muuri": f"{config.npm_cdn}/muuri@0.9.5/dist/muuri.min.js",
            "web-animation": f"{config.npm_cdn}/web-animations-js@2.3.2/web-animations.min.js"
        },
    }

    _template = pathlib.Path(__file__).parent / "editable.html"

    def _update_vars(self):
        ids = {id(obj): next(iter(obj._models)) for obj in self.main}
        self._render_variables['layout'] = layout = {
            ids[iid]: dict(item, id=ids[iid]) for iid, item in self.layout.items()
        }
        self._render_variables['muuri_layout'] = list(layout.values())
        self._render_variables['editable'] = self.editable
        self._render_variables['local_save'] = self.local_save
        self._render_variables['loading_spinner'] = config.loading_spinner
        super()._update_vars()

    def _init_doc(
        self, doc: Document | None = None, comm: Comm | None = None,
        title: str | None = None, notebook: bool = False,
        location: bool | Location = True
    ):
        doc = super()._init_doc(doc, comm, title, notebook, location)
        doc.js_on_event('document_ready', CustomJS(code="""
          window.muuriGrid.getItems().map(item => scroll(item.getElement()));
          for (const root of roots) {
            root.sizing_mode = 'stretch_both';
            if (root.children) {
              for (const child of root) {
                child.sizing_mode = 'stretch_both'
              }
            }
          }
          window.muuriGrid.refreshItems();
          window.muuriGrid.layout();
          window.dispatchEvent(new Event('resize'));
        """, args={'roots': [root for root in doc.roots if 'main' in root.tags]}))
        return doc

    @param.depends('editable', watch=True, on_init=True)
    def _add_editor(self) -> None:
        if not self.editable:
            return
        editor = TemplateEditor()
        editor.param.watch(self._sync_positions, 'layout')
        self._render_items['editor'] = (editor, [])

    def _sync_positions(self, event):
        ids = {mid: id(obj) for obj in self.main for mid in obj._models}
        self.layout.clear()
        self.layout.update({ids[item['id']]: item for item in event.new})
        self.param.trigger('layout')
