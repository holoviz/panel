from panel.custom import Child, JSComponent


class Example(JSComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return children.child
    }"""

Example(child='A Markdown pane!').servable()
