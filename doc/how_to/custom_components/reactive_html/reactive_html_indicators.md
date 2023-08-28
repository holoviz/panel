# Create Indicators With ReactiveHTML

## A Gauge Indicator

Here we create a Gauge indicator that resizes nicely also for if the `height` and `width` is small.

Is inspired by [this codepen](https://codepen.io/fsbraun/pen/XQQpgb)

```{pyodide}
import panel as pn
import param

pn.extension()

CSS = """
.pn-container {height: 100%;width:100%;container-type:size;}
.gauge {
    position: relative;
    border-radius: 50%/100% 100% 0 0;
    background-color: var(--color, #a22);
    overflow: hidden;
    container-type:inline-size;
    margin: auto;
}
.gauge:before{content: "";display: block;padding-top: 50%;}
.gauge .chart {overflow: hidden;}
.gauge .mask {
  position: absolute;
  left: 20%;
  right: 20%;
  bottom: 0;
  top: 40%;
  background-color: #fff;
  border-radius: 50%/100% 100% 0 0;
}

.gauge .percentage {
    position:  absolute;
    top: -1px;
    left: -1px;
    bottom: 0;
    right: -1px;
    background-color: var(--background, #aaa);
    transform:rotate(var(--rotation));
    transform-origin: bottom center;
    transition-duration: 600;
}
.gauge:hover {
    --rotation: 100deg;
}
.gauge .value {
    position:absolute; bottom:0%; left:0;
    width:100%;
    text-align: center;
    font-size: 15cqw;
}
.gauge .min {
    position:absolute;
    bottom:0; left:5%;
}
.gauge .max {
    position:absolute;
    bottom:0; right:5%;
}
"""

class CustomGauge(pn.reactive.ReactiveHTML):
  value = param.Integer(0, bounds=(0,100))
  # color = param.Color("green")
  # background = param.Color("white")

  # _rotation = param.Parameter("0")

  _child_config = {"value": "literal"}
  # _ignored_refs = ("value",)

  # f"<style>{CSS}</style>" +

  _template=  """
<div id="container" class="pn-container">${value}</div>
"""

# <div id="gauge" class="gauge" style="max-width: min(100cqw, 200cqh);max-height: min(50cqw, 100%);--rotation: {{_rotation}}deg; --color:${color}; --background:{{background}};">
#       <div class="percentage" styles="border: 10px solid black"></div>
#       <div class="mask"></div>
#       <span id="value" class="value">{{value}}%</span>
#   </div>

  # @pn.depends("value", watch=True, on_init=True)
  # def _update_rotation(self):
  #     self._rotation="49" # str(int(self.value/100*180))


gauge = CustomGauge(value=55, styles={"border": "2px solid lightgray"}, height=400, sizing_mode="stretch_width")

pn.Column(gauge, gauge.param.value).servable()
```
