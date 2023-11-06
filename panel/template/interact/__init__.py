"""
InteractJS template
"""
import pathlib

from typing import ClassVar, Dict

import param

from ...reactive import ReactiveHTML
from ...theme import Design
from ...theme.native import Native
from ..base import BasicTemplate


class InteractJSEditor(ReactiveHTML):

    state = param.Dict()

    _scripts = {
        'render': """
        for (const obj of document.getElementsByClassName('draggable')) {
          var observer = new MutationObserver(function(mutations) {
            var state = {...data.state}
            for (mutation of mutations) {
              if (mutation.type !== 'attributes')
                continue
              var attr = mutation.attributeName
              if (attr === 'data-x' || attr === 'data-y') {
                var cell_id = mutation.target.getAttribute('cell-id');
                var value = mutation.target.getAttribute(attr);
                if (state[cell_id] == null) {
                  state[cell_id] = {}
                } else {
                  state[cell_id] = {...state[cell_id]}
                }
                state[cell_id][attr.slice(-1)] = parseFloat(value)
              }
            }
            data.state = state
          })
          observer.observe(obj, {attributes: true})
        }
        """
    }


class InteractJSTemplate(BasicTemplate):
    """
    VanillaTemplate is built on top of Vanilla web components.
    """

    design = param.ClassSelector(
        class_=Design,
        default=Native,
        is_instance=False,
        instantiate=False,
        doc="""
        A Design applies a specific design system to a template.""",
    )

    editable = param.Boolean(default=True)

    positions = param.Dict(allow_refs=True)

    _css = pathlib.Path(__file__).parent / "interactjs.css"

    _resources: ClassVar[Dict[str, Dict[str, str]]] = {
        "css": {"lato": "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"},
        "js": {"interactjs": "https://cdn.jsdelivr.net/npm/interactjs@1.10.19/dist/interact.min.js"},
    }

    _template = pathlib.Path(__file__).parent / "interactjs.html"

    @param.depends('editable', watch=True, on_init=True)
    def _add_editor(self) -> None:
        if self.editable:
            editor = InteractJSEditor()
            editor.param.watch(self._sync_positions, 'state')
            ref = f'header-{str(id(editor))}'
            self._render_items[ref] = (editor, ['header'])

    def _sync_positions(self, event):
        self.positions = dict(event.new)
