from panel.custom import Children, JSComponent


class Example(JSComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      const div = document.createElement('div')
      for (const child of children.children) {
        div.appendChild(child)
      }
      return div
    }"""

Example(children=[
    'A Markdown pane!',
    'Another Markdown pane!'
]).servable()
