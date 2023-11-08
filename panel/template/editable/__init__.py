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

    layout = param.List()

    breakpoints = param.List([(500, 0.5), (1000, 0.8), (1200, 1), (1600, 1.5)])

    _scripts = {
        'render': """
        function save_layout() {
          var layout = [];
          var screen_width = window.muuriGrid.getElement().clientWidth
          for (var item of window.muuriGrid.getItems()) {
            var el = item.getElement();
            layout.push({
              id: el.getAttribute('data-id'),
              width: Math.round((item.getWidth() / screen_width) * 100),
              height: item.getHeight(),
              visible: item.isVisible(),
            })
          }
          data.layout = layout
        }
        window.muuriGrid.on('move', save_layout)
        window.muuriGrid.on('hideEnd', save_layout)
        window.resizeableGrid.on('resizeend', save_layout)
        """
    }


class EditableTemplate(VanillaTemplate):

    editable = param.Boolean(default=True)

    layout = param.Dict(allow_refs=True)

    _css = [
        pathlib.Path(__file__).parent.parent / 'vanilla' / "vanilla.css",
        pathlib.Path(__file__).parent / "editable.css"
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
        self._render_variables['muuri_layout'] = [
            dict(item, id=ids[iid]) for iid, item in self.layout.items()
        ]
        super()._update_vars()

    def _init_doc(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        title: Optional[str] = None, notebook: bool = False,
        location: bool | Location=True
    ):
        ret = super()._init_doc(doc, comm, title, notebook, location)
        doc.js_on_event('document_ready', CustomJS(code="""
          for (var item of document.getElementsByClassName('muuri-grid-item')) {
            const child = item.children[1].children[0]
            const bounds = item.getBoundingClientRect()
            const screen_width = window.muuriGrid.getElement().clientWidth
            resize_item(item, Math.round((bounds.width / screen_width) * 100), bounds.height, false)
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
        if self.editable:
            editor = TemplateEditor()
            editor.param.watch(self._sync_positions, 'layout')
            ref = f'header-{str(id(editor))}'
            self._render_items[ref] = (editor, ['header'])

    def _sync_positions(self, event):
        ids = {mid: id(obj) for obj in self.main for mid in obj._models}
        self.layout = {ids[item['id']]: item for item in event.new}
