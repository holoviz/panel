importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.0/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.0/dist/wheels/panel-0.14.0-py3-none-any.whl', 'numpy', 'scikit-image']
  for (const pkg of env_spec) {
    const pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    await self.pyodide.runPythonAsync(`
      import micropip
      await micropip.install('${pkg}');
    `);
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

import base64
import io
import time
from typing import List

import numpy as np
import panel as pn
import param
import PIL
import skimage
from PIL import Image, ImageFilter
from skimage import data, filters
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from skimage.draw import rectangle
from skimage.exposure import rescale_intensity
from skimage.feature import Cascade


pn.extension("terminal", sizing_mode="stretch_width")


class ImageTransform(pn.viewable.Viewer):
    image_type = PIL.Image

    def __init__(self, **params):
        super().__init__(**params)

        self._view = self.create_view()
        with param.edit_constant(self):
            self.name = self.__class__.name.replace("Transform", "")

    def __panel__(self):
        return self._view

    def create_view(self):
        return None

    def run(self, image: str)->str:
        return self.transform(image)
    
    def transform(self, image):
        raise NotImplementedError()

class PILImageTransform(ImageTransform):
    
    @staticmethod
    def to_pil_img(value: str):
        encoded_data = value.split(",")[1]
        base64_decoded = base64.b64decode(encoded_data)
        image = Image.open(io.BytesIO(base64_decoded))
        image.draft("RGB", (400, 400))
        return image
        
    @staticmethod
    def from_pil_img(image: Image):
        jpg_image = image.convert('RGB')

        buff = io.BytesIO()
        jpg_image.save(buff, format="JPEG", mode="L")
        return buff

    def run(self, value: str) -> str:
        pil_img = self.to_pil_img(value)
        
        transformed_image = self.transform(pil_img)
        
        return self.from_pil_img(transformed_image)

class NumpyImageTransform(ImageTransform):
    def run(self, value: str) -> str:
        pil_img = PILImageTransform.to_pil_img(value)
        np_array = np.array(pil_img)
                
        transformed_image = self.transform(np_array)
        
        pil_img = PIL.Image.fromarray((transformed_image * 255).astype(np.uint8)).convert("RGB")
        
        value = PILImageTransform.from_pil_img(pil_img)
        return value

def instantiate(value):
    if isinstance(value, ImageTransform):
        return value
    return value()

class VideoControl(pn.viewable.Viewer):
    video_stream = param.ClassSelector(class_=pn.widgets.VideoStream)

    timeout = param.Integer(1000, bounds=(10, 2000), step=10)
    transform = param.Selector()

    last_update = param.Number()

    def __init__(self, transforms: List[ImageTransform]):
        self.image = pn.pane.JPG(height=400, width=400)
        transforms = [instantiate(transform) for transform in transforms]

        super().__init__()
        self.param.transform.objects = transforms
        self.transform = transforms[0]
        self.settings = pn.Column(
            pn.Param(
                self,
                parameters=["timeout", "transform"],
                expand_button=False,
                expand=False,
                widgets={
                    "transform": {
                        "widget_type": pn.widgets.RadioButtonGroup,
                        "orientation": "vertical",
                    }
                },
            ),
            self._get_transform,
        )
        self.terminal = pn.widgets.Terminal(height=200, width=400, sizing_mode="fixed")
        self.video_stream = pn.widgets.VideoStream(
            name="Video Stream", timeout=1000, height=0, width=0, visible=False
        )

        self.last_update = time.time()

    @pn.depends("transform")
    def _get_transform(self):
        return self.transform

    def __panel__(self):
        return pn.Column(self.video_stream, self.image, self.terminal, height=1200)

    @pn.depends("video_stream.value", watch=True)
    def _handle_stream(self):
        if not self.transform:
            print("no transform select")
            return

        video_stream = self.video_stream
        if not video_stream.value:
            print("no stream yeat")
            return

        if video_stream.paused:
            return

        try:
            video_stream.paused = True
            value = video_stream.value
            
            image = self.transform.run(value)
            self.image.object = image

            now = time.time()
            duration = round(now - self.last_update,2)
            self.terminal.write("updated in " + str(duration) + " seconds\\n")
            self.last_update = now
            
            video_stream.timeout = self.timeout
            video_stream.paused = False
        except PIL.UnidentifiedImageError:
            print("unidentified image")

class BlurTransform(PILImageTransform):
    blur_radius = param.Integer(default=5, bounds=(0, 10))

    def create_view(self):
        return pn.Column(pn.widgets.IntSlider.from_param(self.param.blur_radius))

    def transform(self, image: Image):
        return image.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))


class GrayscaleTransform(NumpyImageTransform):
    def transform(self, image: Image):
        # Ref: https://scikit-image.org/docs/0.15.x/auto_examples/color_exposure/plot_rgb_to_gray.html  # noqa: E501
        grayscale = skimage.color.rgb2gray(image[:,:,:3])
        return skimage.color.gray2rgb(grayscale)  

class SobelTransform(NumpyImageTransform):
    def transform(self, image: Image):
        # Ref: https://scikit-image.org/docs/0.15.x/auto_examples/color_exposure/plot_adapt_rgb.html  # noqa: E501
        @adapt_rgb(each_channel)
        def sobel_each(image):
            return filters.sobel(image)

        return rescale_intensity(1 - sobel_each(image))

@pn.cache()
def get_detector():
        # Load the trained file from the module root.
    trained_file = data.lbp_frontal_face_cascade_filename()

    # Initialize the detector cascade.
    return Cascade(trained_file)


class FaceDetectionTransform(NumpyImageTransform):
    # Ref: https://scikit-image.org/docs/0.15.x/auto_examples/applications/plot_face_detection.html  # noqa: E501
    # TODO: This function is inefficient because detector is loaded
    # TODO: in every frame. Create a cache mechanism.
    
    def transform(self, image: Image):
        detector = get_detector()
        image = image[:,:,:3]
        detected = detector.detect_multi_scale(
            img=image,
            scale_factor=1.4,
            step_ratio=1,
            min_size=(60, 60),
            max_size=(322, 322),
        )

        for patch in detected:
            print(patch)
            rr, cc = rectangle(
                start=(patch["r"], patch["c"]),
                extent=(patch["height"], patch["width"]),
                shape=image.shape[:2],
            )
            image[rr, cc, 0] = 255

        return image


component = VideoControl(transforms=[BlurTransform, GrayscaleTransform, SobelTransform, FaceDetectionTransform])

pn.template.FastListTemplate(
    site="Awesome Panel",
    title="Video Cam",
    sidebar=[component.settings],
    main=[component],
).servable()

# panel convert script2.py --to pyodide-worker --out pyodide --requirements requirements.txt
# panel serve script2.py --autoreload --port 5007

await write_doc()
  `
  const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
  self.postMessage({
    type: 'render',
    docs_json: docs_json,
    render_items: render_items,
    root_ids: root_ids
  });
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()