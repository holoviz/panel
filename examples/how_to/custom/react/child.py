from panel.custom import Child, ReactComponent


class Example(ReactComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return <button>{children.child}</button>
    }"""

Example(child='A Markdown pane!').servable()
