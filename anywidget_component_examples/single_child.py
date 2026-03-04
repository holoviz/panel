"""Single child display using Child() parameter."""
import panel as pn
from panel.custom import AnyWidgetComponent, Child

class SingleChildExample(AnyWidgetComponent):
    child = Child()

    _esm = """
    function render({ model, el }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      el.appendChild(button);
    }

    export default { render };
    """

component = SingleChildExample(child=pn.panel("A **Markdown** pane!"))
