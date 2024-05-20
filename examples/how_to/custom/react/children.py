from panel.custom import Children, ReactComponent


class Example(ReactComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      return <div>{children.children}</div>
    }"""

Example(children=[
    'A Markdown pane!',
    'Another Markdown pane!'
]).servable()
