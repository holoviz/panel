import param

import panel as pn

from panel.custom import ReactComponent, Views


class Example(ReactComponent):

    children = Views()

    _esm = """
    export function render({ children }) {
      return (
        <>
          <div>{children.children}</div>
        </>
      )
    }"""

Example(children=[
    pn.panel('A Markdown pane!'),
    pn.panel('Another Markdown pane!')
]).servable()
