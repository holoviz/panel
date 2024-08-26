from panel.custom import Children, ReactComponent


class Example(ReactComponent):

    children = Children()

    _esm = """
    export function render({ model }) {
      return <div>{model.get_child("children")}</div>
    }"""

Example(children=[
    'A Markdown pane!',
    'Another Markdown pane!'
]).servable()
