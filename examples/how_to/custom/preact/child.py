import param

import panel as pn

from panel.custom import PreactComponent, View


class Example(PreactComponent):

    child = View()

    _esm = """
    export function render({ html, children }) {
      return html`<button ref=${ref => ref && ref.appendChild(children.child)}></button>`
    }"""

Example(child=pn.panel('A Markdown pane!')).servable()
