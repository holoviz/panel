import panel as pn

pn.extension(sizing_mode="stretch_width")

pn.Column(
    "# Hello from External File!",
    "This code was loaded via the `src` attribute.",
    pn.widgets.IntSlider(name="Slider", start=0, end=100, value=50),
).servable()
