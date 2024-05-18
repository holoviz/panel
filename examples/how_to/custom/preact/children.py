import param

import panel as pn

from panel import JSComponent


class Example(JSComponent):

    children = param.List(item_type=pn.viewable.Viewable)

    _esm = """
    export function render({ children }) {
      const div = document.createElement('div')
      for (const child of children.children) {
        div.appendChild(child)
      }
      return div
    }"""

Example(children=[
    pn.panel('A Markdown pane!'),
    pn.panel('Another Markdown pane!')
]).servable()
