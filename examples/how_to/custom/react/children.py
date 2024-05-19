import param

import panel as pn

from panel.custom import ReactComponent


class Example(ReactComponent):

    children = param.List(item_type=pn.viewable.Viewable)

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
