"""Counter widget with inline CSS via _stylesheets."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class StyledCounterWidget(AnyWidgetComponent):
    _esm = """
    function render({ model, el }) {
      let count = () => model.get("value");
      let btn = document.createElement("button");
      btn.innerHTML = `count is ${count()}`;
      btn.addEventListener("click", () => {
        model.set("value", count() + 1);
        model.save_changes();
      });
      model.on("change:value", () => {
        btn.innerHTML = `count is ${count()}`;
      });
      el.appendChild(btn);
    }
    export default { render };
    """
    _stylesheets = [
        """
        button { color: white; font-size: 1.75rem; background-color: #ea580c;
                 padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; }
        button:hover { background-color: #9a3412; }
        """
    ]
    value = param.Integer()

component = StyledCounterWidget()
