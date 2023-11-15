"""
Editable template
"""
from __future__ import annotations

import pathlib

from typing import (
    TYPE_CHECKING, ClassVar, Dict, Optional,
)

import param

from bokeh.models import CustomJS

from ...reactive import ReactiveHTML
from ..vanilla import VanillaTemplate

if TYPE_CHECKING:
    from bokeh.document import Document
    from pyviz_comms import Comm

    from ..io.location import Location


class TemplateEditor(ReactiveHTML):
    """
    Component responsible for watching the template for changes and syncing
    the current layout state with Python.
    """

    layout = param.List()

    _scripts = {
        'render': """
        var grid = window.muuriGrid;
        function save_layout() {
          var layout = [];
          var screen_width = grid.getElement().clientWidth-20;
          for (var item of grid.getItems()) {
            var el = item.getElement();
            const style = getComputedStyle(el)
            const top = parseInt(style.getPropertyValue('padding-top').slice(0, -2))
            const bottom = parseInt(style.getPropertyValue('padding-bottom').slice(0, -2))
            layout.push({
              id: el.getAttribute('data-id'),
              width: (item.getWidth() / screen_width) * 100,
              height: item.getHeight()-top-bottom,
              visible: item.isVisible(),
            })
          }
          data.layout = layout
        }
        grid.on('layoutEnd', save_layout)
        window.resizeableGrid.on('resizeend', save_layout)
        """
    }


class EditableTemplate(VanillaTemplate):
    """
    The EditableTemplate builds on top of Muuri and interact.js to
    allow interactively dragging, resizing and hiding components on a
    grid.
    """

    editable = param.Boolean(default=True, doc="""
      Whether the template layout should be editable.""")

    layout = param.Dict(default={}, allow_refs=True, doc="""
      The layout definition of the template indexed by the id of
      each component in the main area.""")

    _css = [
        pathlib.Path(__file__).parent.parent / 'vanilla' / "vanilla.css",
        pathlib.Path(__file__).parent / 'editable.css'
    ]

    _resources: ClassVar[Dict[str, Dict[str, str]]] = {
        "css": {"lato": "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"},
        "js": {
            "interactjs": "https://cdn.jsdelivr.net/npm/interactjs@1.10.19/dist/interact.min.js",
            "muuri": "https://cdn.jsdelivr.net/npm/muuri@0.9.5/dist/muuri.min.js",
            "web-animation": "https://cdn.jsdelivr.net/npm/web-animations-js@2.3.2/web-animations.min.js"
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
        super()._update_vars()

    def _init_doc(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        title: Optional[str] = None, notebook: bool = False,
        location: bool | Location=True
    ):
        ret = super()._init_doc(doc, comm, title, notebook, location)
        doc.js_on_event('document_ready', CustomJS(code="""
          for (const item of document.getElementsByClassName('muuri-grid-item')) {
            const style = getComputedStyle(item)
            const top = parseInt(style.getPropertyValue('padding-top').slice(0, -2))
            const bottom = parseInt(style.getPropertyValue('padding-bottom').slice(0, -2))
            const child = item.children[1].children[0];
            const bounds = item.getBoundingClientRect();
            const screen_width = window.muuriGrid.getElement().clientWidth-20;
            const relative_width = Math.round((bounds.width / (screen_width)) * 100);
            resize_item(item, relative_width, bounds.height-top-bottom, false)
          }
          for (var root of roots) {
            if (root.tags.includes('main')) {
              root.sizing_mode = 'stretch_both'
              if (root.children) {
                for (var child of root) {
                  child.sizing_mode = 'stretch_both'
                }
              }
            }
          }
          window.muuriGrid.refreshItems();
          window.muuriGrid.layout();
        """, args={'roots': doc.roots}))
        return ret

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
