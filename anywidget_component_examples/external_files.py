"""Counter button with _esm/_stylesheets as file paths."""
from pathlib import Path
import param
import panel as pn
from panel.custom import AnyWidgetComponent

HERE = Path(__file__).parent

class CounterButton(AnyWidgetComponent):
    value = param.Integer()
    _esm = HERE / "counter_button.js"
    _stylesheets = [HERE / "counter_button.css"]

component = CounterButton()
