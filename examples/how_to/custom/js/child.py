import param

import panel as pn

from panel.custom import JSComponent


class Example(JSComponent):

    child = param.ClassSelector(class_=pn.viewable.Viewable)

    _esm = """
    export function render({ children }) {
      return children.child
    }"""

Example(child=pn.panel('A Markdown pane!')).servable()
