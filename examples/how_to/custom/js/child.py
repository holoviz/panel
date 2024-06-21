from panel.custom import Child, JSComponent


class Example(JSComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      return model.get_child('child')
    }"""

Example(child='A Markdown pane!').servable()
