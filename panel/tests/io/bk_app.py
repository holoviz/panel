"""Minimal Bokeh Hello World Example"""
from bokeh.models import Div
from bokeh.plotting import curdoc

app = curdoc()
model = Div(text="<h1>Hello Bokeh World from .py Code File</h1>", sizing_mode="stretch_width")
app.add_root(model)