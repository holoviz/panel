"""ChartJS pane using Chart.js CDN library."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class ChartJSComponent(AnyWidgetComponent):
    object = param.Dict()

    _esm = """
import { Chart } from "https://esm.sh/chart.js/auto"

function render({ model, el }) {
  const canvasEl = document.createElement('canvas')
  el.append(canvasEl)
  const create_chart = () => new Chart(canvasEl.getContext('2d'), model.get("object"))
  let chart = create_chart()
  model.on("change:object", () => {
    chart.destroy()
    chart = create_chart()
  })
  return () => chart.destroy()
}

export default { render };
"""

component = ChartJSComponent(
    object={
        "type": "line",
        "data": {
            "labels": ["January", "February", "March", "April", "May", "June", "July"],
            "datasets": [
                {
                    "label": "Data",
                    "backgroundColor": "rgb(255, 99, 132)",
                    "borderColor": "rgb(255, 99, 132)",
                    "data": [0, 10, 5, 2, 20, 30, 45],
                }
            ],
        },
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
        },
    },
    height=400,
    sizing_mode="stretch_width",
)
