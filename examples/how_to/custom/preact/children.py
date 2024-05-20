from panel.custom import Children, PreactComponent


class Example(PreactComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      return html`<div>${children.children}</div>`
    }"""

Example(children=[
    'A Markdown pane!',
    'Another Markdown pane!'
]).servable()
