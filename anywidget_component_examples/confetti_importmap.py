"""Confetti button using _importmap for import aliasing."""
import panel as pn
from panel.custom import AnyWidgetComponent

class ConfettiButton(AnyWidgetComponent):
    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "canvas-confetti";

    function render({ el }) {
      let btn = document.createElement("button");
      btn.innerHTML = "Click Me";
      btn.addEventListener("click", () => {
        confetti();
      });
      el.appendChild(btn);
    }
    export default { render }
    """

component = ConfettiButton()
