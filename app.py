import numpy as np

from matplotlib.figure import Figure

import panel as pn

ACCENT = "golden rod"

pn.extension(sizing_mode="stretch_width")

data = np.random.normal(1, 1, size=100)
fig = Figure(figsize=(8,4))
ax = fig.subplots()
ax.hist(data, bins=20, color=ACCENT)

component = pn.pane.Matplotlib(fig, format='svg', sizing_mode='scale_both')

pn.template.FastListTemplate(
    title="My App", sidebar=["# Settings"], main=[component], accent=ACCENT
).servable()
