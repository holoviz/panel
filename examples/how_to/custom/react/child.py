from panel.custom import Child, ReactComponent


class Example(ReactComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      return <button>{model.get_child("child")}</button>
    }"""

Example(child='A Markdown pane!').servable()
