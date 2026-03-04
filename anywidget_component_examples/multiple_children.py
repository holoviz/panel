"""Multiple children display using Children() parameter."""
import panel as pn
from panel.custom import AnyWidgetComponent, Children

class MultiChildExample(AnyWidgetComponent):
    objects = Children()

    _esm = """
    function render({ model, el }) {
      const div = document.createElement('div')
      div.append(...model.get_child("objects"))
      el.appendChild(div);
    }

    export default { render };
    """

component = MultiChildExample(
    objects=[
        pn.panel("A **Markdown** pane!"),
        pn.widgets.Button(name="Click me!"),
        {"text": "I'm shown as a JSON Pane"},
    ]
)
