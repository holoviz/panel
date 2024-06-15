# Original Source: https://github.com/opengeos/solara-geospatial/blob/main/pages/01_leafmap.py
import leafmap
import param

from leafmap.toolbar import change_basemap

import panel as pn

from panel.ipywidget import WidgetViewer

pn.extension("ipywidgets")

class Map(leafmap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add what you want below
        self.add_basemap("OpenTopoMap")
        change_basemap(self)

widget = Map(  # type: ignore
    zoom=2,
    center=(20,0),
    scroll_wheel_zoom=True,
    toolbar_ctrl=False,
    data_ctrl=False,
)

class MapViewer(WidgetViewer):
    zoom = param.Number(default=2, bounds=(0,24), step=1)
    center = param.List([20,0])

viewer = MapViewer(model=widget, height=500, sizing_mode="stretch_width")

layout = pn.Column(
    viewer,
    pn.Row(
        viewer.param.zoom,
        viewer.param.center,
        pn.pane.Markdown(pn.rx("Zoom: {zoom}").format(zoom=viewer.param.zoom)),
        pn.pane.Markdown(pn.rx("Center: {center}").format(center=viewer.param.center)),
    ),
)

pn.template.FastListTemplate(
    site="🌎 Panel Geospatial",
    site_url="./",
    title="Leafmap",
    main=[layout],
    main_layout=None,
    accent="teal",
).servable()
