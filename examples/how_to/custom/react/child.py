import param

import panel as pn

from panel.custom import ReactComponent, View


class Example(ReactComponent):

    child = View()

    _esm = """
    export function render({ html, children }) {
      return (
        <>
          <button>{children.child}</button>
        </>
      )
    }"""

Example(child=pn.panel('A Markdown pane!')).servable()
