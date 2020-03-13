# "https://modelviewer.dev/examples/tester.html"

import panel as pn
import param
pn.config.sizing_mode="stretch_width"
js = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.js"></script>
<script nomodule src="https://unpkg.com/@google/model-viewer/dist/model-viewer-legacy.js"></script>
"""

# js = """
# <script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
# <script src="https://wiredjs.com/dist/showcase.min.js"></script>
# """

js_pane = pn.pane.HTML(js)

# html="""
# <model-viewer src="https://modelviewer.dev/shared-assets/models/Astronaut.glb" alt="A 3D model of an astronaut"
# auto-rotate camera-controls>
# </model-viewer>
# """
# model_viewer_pane = pn.pane.WebComponent(html=html)

# settings_pane = pn.Param()

# # auto-rotate camera-controls>"""
html = '<wired-radio>Radio Button Label</wired-radio>'
html = """<span>hello</span>"""
html="""
<model-viewer src="https://modelviewer.dev/shared-assets/models/Astronaut.glb" alt="A 3D model of an astronaut"
auto-rotate camera-controls>
</model-viewer>
"""

# parameters_to_watch={"auto-rotate": "auto_rotate"}

# src_objects = [flight_helmet_src, astronaut_src]

# class ModelViewer(pn.pane.WebComponent):
#     html = param.String(html)
#     parameters_to_watch = param.Dict(parameters_to_watch)

#     # src = param.ObjectSelector(default=flight_helmet_src, objects=src_objects)
#     auto_rotate = param.Boolean(default=True)

# model_viewer_pane = ModelViewer(height=400)
# settings_pane = pn.Param(model_viewer_pane.param, parameters=["html", "auto_rotate"])

# app = pn.Column(
#     js_pane,
#     model_viewer_pane,
#     settings_pane,
# )
# app.servable()

astronaut_src = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
flight_helmet_src="https://modelviewer.dev/shared-assets/models/glTF-Sample-Models/2.0/FlightHelmet/glTF/FlightHelmet.gltf"

class ModelViewer(pn.pane.WebComponent):
    """A Wired ModelViewer"""
    html = param.String(html)
    properties_to_watch= param.Dict({"src": "src", "exposure": "exposure"})

    src = param.String(astronaut_src)
    exposure = param.Number(1.0, bounds=(0, 2))


model_viewer = ModelViewer(min_height=200, width=300, src=flight_helmet_src)

pn.Row(
    js_pane,
    model_viewer, pn.Param(model_viewer, parameters=["exposure"]),
).servable()