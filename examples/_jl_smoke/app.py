import panel as pn
pn.extension()
slider = pn.widgets.IntSlider(name="Value", start=0, end=10, value=3)
text = pn.bind(lambda v: f"Selected: {v}", slider)
pn.Column("# Panel Preview smoke", slider, text).servable()
