import panel as pn

from panel import JSComponent

pn.extension()

class ConfettiButton(JSComponent):

    _importmap = {
        "imports": {
            "confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = """
    import confetti from "confetti";

    export function render() {
        let btn = document.createElement("button");
        btn.innerHTML = `Click Me`;
        btn.addEventListener("click", () => {
            confetti()
        });
        return btn
    }
    """

ConfettiButton().servable()
