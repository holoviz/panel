import panel as pn
import numpy as np
import holoviews as hv

pn.extension(sizing_mode="stretch_width")

template = pn.template.FastListTemplate(
    site="Awesome Panel", title="New Accent Color",
    main=[pn.widgets.Button(name="Click Me", button_type="primary")],
)
pn.Param(template, sorted=True).servable()