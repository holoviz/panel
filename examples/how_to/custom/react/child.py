import param

import panel as pn

from panel.custom import ReactComponent


class Example(ReactComponent):

    child = param.ClassSelector(class_=pn.viewable.Viewable)

    _esm = """
    export function render({ html, children }) {
      return (
        <>
          <button>{children.child}</button>
        </>
      )
    }"""

Example(child=pn.panel('A Markdown pane!')).servable()
