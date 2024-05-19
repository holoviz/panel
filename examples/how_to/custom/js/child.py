import param

import panel as pn

from panel.custom import JSComponent, View


class Example(JSComponent):

    child = View()

    _esm = """
    export function render({ children }) {
      return children.child
    }"""

Example(child=pn.panel('A Markdown pane!')).servable()
