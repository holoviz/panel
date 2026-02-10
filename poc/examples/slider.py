import panel as pn

pn.extension(sizing_mode="stretch_width")

slider = pn.widgets.FloatSlider(name="Value", start=0, end=10, step=0.1, value=5.0)

pn.Column(
    "# Slider Demo",
    slider,
    pn.bind(lambda v: pn.pane.Markdown(f"**Current value:** {v:.1f}"), slider),
).servable()
