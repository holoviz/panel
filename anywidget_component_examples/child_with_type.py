"""Child with type constraint using Child(class_=...)."""
import panel as pn
from panel.custom import AnyWidgetComponent, Child

class TypedChildExample(AnyWidgetComponent):
    child = Child(class_=pn.pane.Markdown)

    _esm = """
    function render({ model, el }) {
      const button = document.createElement("button");
      button.append(model.get_child("child"))
      el.appendChild(button);
    }

    export default { render };
    """

component = TypedChildExample(child=pn.panel("A **Markdown** pane!"))
