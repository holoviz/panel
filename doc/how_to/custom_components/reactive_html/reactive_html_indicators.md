# Create Indicators With ReactiveHTML

In this guide we will show you how to build custom indicators using `ReactiveHTML`.

## Basic Progress Indicator

Here we create a basic progress indicator

```{pyodide}
import param
import panel as pn
from panel.reactive import ReactiveHTML

pn.extension()

class CustomProgress(ReactiveHTML):
  value = param.Integer(0, bounds=(0,100))
  color = param.Color("#007bff")

  _template=  """
<div id="progress-bar" style="background-color: ${color}; height: 100%; width: ${value}%;"></div>
"""

progress = CustomProgress(
  value=55, styles={"border": "2px solid lightgray"}, height=100, sizing_mode="stretch_width"
)
pn.Column(progress, progress.param.value, progress.param.color).servable()
```

## Advanced Progress Indicator

Here we create an advanced progress indicator

```{pyodide}
import random
import pandas as pd
import param
import panel as pn


class ArcProgressIndicator(pn.reactive.ReactiveHTML):

    progress = param.Number(default=0, bounds=(0, 100))

    transition_duration = param.Number(default=0.5, bounds=(0, None))

    format_options = param.Dict(
        default={
            "locale": "en-US",
            "style": "percent",
            "minimumIntegerDigits": "1",
            "maximumIntegerDigits": "3",
            "minimumFractionDigits": "1",
            "maximumFractionDigits": "1",
        }
    )

    text_style = param.Dict(
        default={
            "font-size": 4.5,
            "text-anchor": "middle",
            "letter-spacing": -0.2,
        }
    )

    empty_color = param.Color(default="#e8f6fd")

    fill_color = param.Color(default="#2a87d8")

    use_gradient = param.Boolean(default=False)

    gradient = param.Parameter(
        default=[{"stop": 0, "color": "green"}, {"stop": 1, "color": "red"}]
    )

    annotations = param.Parameter(default=[])

    viewbox = param.List(default=[0, -1, 20, 10], constant=True)

    _template = """
    <div id="container">
        <svg id="svg" height="100%" width="100%" viewBox="0 -1 20 10" style="display: block;">
          <defs>
              <linearGradient id="grad">
                <stop offset="0" style="stop-color:black" />
                <stop offset="1" style="stop-color:magenta" />
              </linearGradient>
          </defs>
        </svg>
    </div>
    """

    _scripts = {
        "render": """
            state.initialized = false
            state.GradientReader = function(colorStops) {

                const canvas = document.createElement('canvas');   // create canvas element
                const ctx = canvas.getContext('2d');               // get context
                const gr = ctx.createLinearGradient(0, 0, 101, 0); // create a gradient

                canvas.width = 101;                                // 101 pixels incl.
                canvas.height = 1;                                 // as the gradient

                for (const { stop, color } of colorStops) {               // add color stops
                    gr.addColorStop(stop, color);
                }

                ctx.fillStyle = gr;                                // set as fill style
                ctx.fillRect(0, 0, 101, 1);                        // draw a single line

                // method to get color of gradient at % position [0, 100]
                return {
                    getColor: (pst) => {
                        const color_array = ctx.getImageData(pst|0, 0, 1, 1).data
                        return `rgb(${color_array[0]}, ${color_array[1]}, ${color_array[2]})`
                    }
                };
            }
            const empty_path = document.createElementNS("http://www.w3.org/2000/svg", "path")
            empty_path.setAttribute("d", "M1 9 A 8 8 0 1 1 19 9")
            empty_path.setAttribute("fill", "none")
            empty_path.setAttribute("stroke-width", "1.5")
            state.empty_path = empty_path

            const fill_path = empty_path.cloneNode()
            state.fill_path = fill_path

            text = document.createElementNS("http://www.w3.org/2000/svg", "text")
            text.setAttribute("y","8.9")
            text.setAttribute("x","10")
            self.text_style()
            state.text = text

            //path used to
            const external_path = document.createElementNS("http://www.w3.org/2000/svg", "path")
            external_path.setAttribute("d", "M0.25 9 A 8.75 8.75 0 1 1 19.75 9")
            state.external_path = external_path

            svg.appendChild(empty_path)
            svg.appendChild(fill_path)
            svg.appendChild(text)

            self.viewbox()
            self.transition_duration()
            self.empty_color()
            self.fill_color()
            self.format_options()
            self.gradient()
            self.progress()
            self.annotations()
            state.initialized = true
        """,
        "annotations": """
            const path_len = state.empty_path.getTotalLength()
            const tot_len = state.external_path.getTotalLength()
            svg.querySelectorAll(".ArcProgressIndicator_annotation").forEach((node) => node.remove())
            const annotations = data.annotations
            annotations.forEach((annotation) => {
                const {progress, text, tick_width, text_size} = annotation
                const annotation_position = state.external_path.getPointAtLength(tot_len * progress/100);

                const annot_tick = state.empty_path.cloneNode()
                annot_tick.setAttribute("class", "ArcProgressIndicator_annotation")
                annot_tick.setAttribute("stroke-dasharray", `${tick_width} ${path_len}`)
                annot_tick.setAttribute("stroke-dashoffset", `${-(path_len * progress/100 - tick_width/2)}`)
                annot_tick.setAttribute("stroke", "black")

                const annot_text = document.createElementNS("http://www.w3.org/2000/svg", "text")
                annot_text.setAttribute("class", "ArcProgressIndicator_annotation")
                annot_text.setAttribute("x",annotation_position.x)
                annot_text.setAttribute("y",annotation_position.y)
                annot_text.setAttribute("style",`font-size:${text_size};text-anchor:${progress>50 ? "start" : "end"}`)

                const textNode = document.createTextNode(text)
                annot_text.appendChild(textNode)

                svg.appendChild(annot_tick)
                svg.appendChild(annot_text)
            })


        """,
        "progress": """
            const textNode = document.createTextNode(`${state.formatter.format(data.progress / (state.formatter.resolvedOptions().style=="percent" ? 100 : 1))}`)

            if(state.text.firstChild)
                state.text.firstChild.replaceWith(textNode)
            else
                text.appendChild(textNode)
            const path_len = state.empty_path.getTotalLength()
            state.fill_path.setAttribute("stroke-dasharray", `${path_len * data.progress/100} ${path_len}`)
            const current_color = data.use_gradient ? state.gr.getColor(data.progress) : data.fill_color

            if(!state.text_style || !("fill" in state.text_style))
                state.text.setAttribute("fill", current_color)
        """,
        "transition_duration": """
            state.fill_path.setAttribute("style", `transition: stroke-dasharray ${data.transition_duration}s`)
        """,
        "format_options": """
            state.formatter = new Intl.NumberFormat(data.format_options.locale, data.format_options)
            if (state.initialized)
                self.progress()
        """,
        "text_style": """
                text.setAttribute("style", Object.entries(data.text_style).map(([k, v]) => `${k}:${v}`).join(';'))
            """,
        "empty_color": """
            state.empty_path.setAttribute("stroke", data.empty_color)
        """,
        "fill_color": """
            if (data.use_gradient)
                state.fill_path.setAttribute("stroke", `url(#grad-${data.id}`)
            else
                state.fill_path.setAttribute("stroke", data.fill_color)
        """,
        "use_gradient": """
            self.fill_color()
            if (state.initialized)
                self.progress()
        """,
        "gradient": """
            const gradientNode = container.querySelector("linearGradient")
            gradientNode.querySelectorAll("stop").forEach((stop) => gradientNode.removeChild(stop))
            const list_gradient_values = data.gradient
            list_gradient_values.forEach((elem) => {
                const stopNode = document.createElementNS("http://www.w3.org/2000/svg", "stop")
                stopNode.setAttribute("offset", `${elem.stop}`)
                stopNode.setAttribute("stop-color", `${elem.color}`)
                gradientNode.appendChild(stopNode)
            })
            state.gr = new state.GradientReader(data.gradient)
            if (state.initialized)
                self.progress()
        """,
        "viewbox": """
            svg.setAttribute("viewBox", data.viewbox.join(" "))
        """,
    }

    def __init__(self, **params):
        if "text_style" in params:
            default_text_style = dict(self.param.text_style.default)
            default_text_style.update(params.get("text_style"))
            params["text_style"] = default_text_style
        if "format_options" in params:
            default_format_options = dict(self.param.format_options.default)
            default_format_options.update(params.get("format_options"))
            params["format_options"] = default_format_options

        super().__init__(**params)
        self._on_use_gradient_change()

    @pn.depends("use_gradient", watch=True)
    def _on_use_gradient_change(self):
        if self.use_gradient:
            self.param.fill_color.precedence = -1
            self.param.gradient.precedence = 1
        else:
            self.param.fill_color.precedence = 1
            self.param.gradient.precedence = -1


indicator = ArcProgressIndicator(
    progress=10,
    styles={"background": "#efebeb"},
    use_gradient=True,
    text_style={"fill": "gray"},
    format_options={"style": "percent"},
    viewbox=[-2, -2, 24, 11],
    annotations=[
        {"progress": 0, "text": "0%", "tick_width": 0.2, "text_size": 0.8},
        {"progress": 10, "text": "10%", "tick_width": 0.1, "text_size": 1},
        {"progress": 100, "text": "100%", "tick_width": 0.2, "text_size": 0.8},
    ],
)
pn.Row(indicator.controls()[0], indicator).servable()
```
