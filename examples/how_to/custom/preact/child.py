from panel.custom import Child, PreactComponent


class Example(PreactComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return html`<button>${children.child}</button>`
    }"""

Example(child='A Markdown pane!').servable()
