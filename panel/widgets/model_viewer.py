# "https://modelviewer.dev/examples/tester.html"

import panel as pn
import param

JAVASCRIPT = """
<script src="https://unpkg.com/@webcomponents/webcomponentsjs@2.2.7/webcomponents-loader.js"></script>
<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.js"></script>
<script nomodule src="https://unpkg.com/@google/model-viewer/dist/model-viewer-legacy.js"></script>
"""

HTML="""
<model-viewer src="https://modelviewer.dev/shared-assets/models/Astronaut.glb" alt="A 3D model of an astronaut"
auto-rotate camera-controls style="height:100%,width:100%;">
</model-viewer>
"""

DEFAULT_SRC="https://modelviewer.dev/shared-assets/models/glTF-Sample-Models/2.0/FlightHelmet/glTF/FlightHelmet.gltf"

class ModelViewer(pn.pane.WebComponent):
    """A Wired ModelViewer"""
    html = param.String(HTML)
    properties_to_watch= param.Dict({"src": "src", "exposure": "exposure"})

    src = param.String(DEFAULT_SRC)
    exposure = param.Number(1.0, bounds=(0, 2))

