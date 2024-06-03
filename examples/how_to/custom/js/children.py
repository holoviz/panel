from panel.custom import Children, JSComponent


class Example(JSComponent):

    children = Children()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      div.append(...model.get_child('children'))
      return div
    }"""

Example(children=[
    'A Markdown pane!',
    'Another Markdown pane!'
]).servable()
