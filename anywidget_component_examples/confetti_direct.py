"""Confetti button using direct CDN URL import."""
import panel as pn
from panel.custom import AnyWidgetComponent

class ConfettiButton(AnyWidgetComponent):
    _esm = """
    import confetti from "https://esm.sh/canvas-confetti@1.6.0";

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
