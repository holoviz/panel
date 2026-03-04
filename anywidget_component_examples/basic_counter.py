"""Basic counter widget — minimal ESM, click handler, model.get/set/save_changes."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class CounterWidget(AnyWidgetComponent):
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
    value = param.Integer()

component = CounterWidget()
