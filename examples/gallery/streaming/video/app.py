import base64
import io
import time

from typing import List

import numpy as np
import param
import PIL
import skimage

from PIL import Image, ImageFilter
from skimage import data, filters
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from skimage.draw import rectangle
from skimage.exposure import rescale_intensity
from skimage.feature import Cascade

import panel as pn

pn.extension("terminal", sizing_mode="stretch_width")

HEIGHT = 400
WIDTH = 400
TIMEOUT = 250

def instantiate(value, **params):
    if isinstance(value, ImageTransform):
        return value
    return value(**params)

class Timer(pn.viewable.Viewer):
    trends = param.Dict()

    def __init__(self, layout=pn.Row, **params):
        super().__init__()

        self.last_updates=dict()
        self.trends=dict()

        self._layout = instantiate(layout, **params)

    def timeit(self, channel, func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = round(end-start,2)
        self.report(channel=channel, duration=duration)
        return result

    def incit(self, channel):
        start = self.last_updates.get(channel, time.time())
        end = time.time()
        duration = round(end-start,2)
        self.report(channel=channel, duration=duration)
        self.last_updates[channel]=end

    def report(self, channel, duration):
        if not channel in self.trends:
            self.trends[channel] = pn.indicators.Trend(title=channel, data={"x": [1], "y": [duration]}, height=100, width=150, sizing_mode="fixed")
            self.param.trigger("trends")
        else:
            trend = self.trends[channel]
            next_x = max(trend.data["x"])+1
            trend.stream({"x": [next_x], "y": [duration]}, rollover=10)

    @pn.depends("trends")
    def _panel(self):
        self._layout[:]=list(self.trends.values())
        return self._layout

    def __panel__(self):
        return self._panel

    

class ImageTransform(pn.viewable.Viewer):
    """Base class for image transforms."""
    def __init__(self, **params):
        super().__init__(**params)

        with param.edit_constant(self):
            self.name = self.__class__.name.replace("Transform", "")
        self._view = self.create_view()

    def __panel__(self):
        print("__panel__", self.name)
        return self._view

    def run(self, image: str, height: int=HEIGHT, width: int=WIDTH)->str:
        """Transforms the base64 encoded png to a base64 encoded jpg"""
        return self.transform(image)
        
    def create_view(self):
        """Creates a view of the parameters of the transform to enable the user to configure them"""
        return pn.Param(self, name=self.name)
    
    def transform(self, image):
        """Transforms the image"""
        raise NotImplementedError()

class PILImageTransform(ImageTransform):
    """Base class for PIL image transforms"""
    
    @staticmethod
    def to_pil_img(value: str, height=HEIGHT, width=WIDTH):
        encoded_data = value.split(",")[1]
        base64_decoded = base64.b64decode(encoded_data)
        image = Image.open(io.BytesIO(base64_decoded))
        image.draft("RGB", (height, width))
        return image
        
    @staticmethod
    def from_pil_img(image: Image):
        buff = io.BytesIO()
        image.save(buff, format="JPEG")
        return buff

    def run(self, value: str, height: int=HEIGHT, width: int=WIDTH) -> str:
        pil_img = self.to_pil_img(value, height=height, width=width)
        
        transformed_image = self.transform(pil_img)
        
        return self.from_pil_img(transformed_image)

class NumpyImageTransform(ImageTransform):
    @staticmethod
    def to_np_ndarray(value: str, height=HEIGHT, width=WIDTH)->np.ndarray:
        pil_img = PILImageTransform.to_pil_img(value, height=height, width=width)
        return np.array(pil_img)

    @staticmethod
    def from_np_ndarray(value: np.ndarray)->str:
        if value.dtype == np.dtype('float64'):
            value = (value * 255).astype(np.uint8)
        pil_img = PIL.Image.fromarray(value)
        return PILImageTransform.from_pil_img(pil_img)

    def run(self, value: str, height: int=HEIGHT, width: int=WIDTH) -> str:
        np_array = self.to_np_ndarray(value, height=height, width=width)
                
        transformed_image = self.transform(np_array)
        
        return self.from_np_ndarray(transformed_image)

class VideoControl(pn.viewable.Viewer):
    video_stream = param.ClassSelector(class_=pn.widgets.VideoStream)

    height = param.Integer(HEIGHT, bounds=(10,2000), step=10)
    width = param.Integer(WIDTH, bounds=(10,2000), step=10)
    
    transform = param.Selector()

    def __init__(self, transforms: List[ImageTransform], timeout=TIMEOUT, paused=False):
        self.image = pn.pane.JPG(height=self.height, width=self.width, sizing_mode="fixed")
        transforms = [instantiate(transform) for transform in transforms]
        self._updating = False

        super().__init__()
        self.param.transform.objects = transforms
        self.transform = transforms[0]
        self.timer = Timer(sizing_mode="stretch_width")
        self.video_stream = pn.widgets.VideoStream(
            name="Video Stream", timeout=timeout, paused=paused, height=0, width=0, visible=False, format="jpeg"
        )
        self.settings = pn.Column(
            pn.Param(
                self.video_stream,
                parameters=["timeout", "paused"],
                widgets={
                    "timeout": {
                        "widget_type": pn.widgets.IntSlider,
                        "start": 10, "end": 2000, "step": 10,
                    }
                },
            ),
            self.timer,
            pn.Param(
                self,
                parameters=["height", "width"],
                name="Image"
            ),
            pn.Param(
                self,
                parameters=["transform"],
                expand_button=False,
                expand=False,
                widgets={
                    "transform": {
                        "widget_type": pn.widgets.RadioButtonGroup,
                        "orientation": "vertical",
                    }
                },
                name="Transform"
            ),
            self._get_transform,
        )
        
    @pn.depends("height", "width", watch=True)
    def _update_height_width(self):
        self.image.height=self.height
        self.image.width=self.width
        

    @pn.depends("transform")
    def _get_transform(self):
        # Hack: returning self.transform stops working after some changes
        return self.transform._view

    def __panel__(self):
        return pn.Row(self.video_stream, pn.layout.HSpacer(), self.image, pn.layout.HSpacer(), sizing_mode="stretch_width", align="center",  )

    @pn.depends("video_stream.value", watch=True)
    def _handle_stream(self):
        if self._updating:
            return

        self._updating = True
        if self.transform and self.video_stream.value:    
            value = self.video_stream.value
            try:
                image = self.timer.timeit(channel="Transform", func=self.transform.run, value=value, height=self.height, width=self.width)
                self.image.object = image
            except PIL.UnidentifiedImageError:
                print("unidentified image")
            
            self.timer.incit("last update")
        self._updating = False
        

class GaussianBlur(PILImageTransform):
    radius = param.Integer(default=2, bounds=(0, 10))

    def transform(self, image: Image):
        return image.filter(ImageFilter.GaussianBlur(radius=self.radius))


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
    """Face detection using a cascade classifier.
    
    Ref: https://scikit-image.org/docs/0.15.x/auto_examples/applications/plot_face_detection.html
    """
    scale_factor = param.Number(1.4, bounds=(0.1, 2.0), step=0.1)
    step_ratio = param.Integer(1, bounds=(1,10))
    size_x = param.Range(default=(60,322), bounds=(10,500))
    size_y = param.Range(default=(60,322), bounds=(10,500))

    def transform(self, image: Image):
        """Face detection using a cascade classifier"""

        detector = get_detector()
        detected = detector.detect_multi_scale(
            img=image,
            scale_factor=self.scale_factor,
            step_ratio=self.step_ratio,
            min_size=(self.size_x[0], self.size_y[0]),
            max_size=(self.size_x[1], self.size_y[1]),
        )

        for patch in detected:
            rr, cc = rectangle(
                start=(patch["r"], patch["c"]),
                extent=(patch["height"], patch["width"]),
                shape=image.shape[:2],
            )
            image[rr, cc, 0] = 200

        return image


component = VideoControl(transforms=[GaussianBlur, GrayscaleTransform, SobelTransform, FaceDetectionTransform])

pn.template.FastListTemplate(
    site="Awesome Panel",
    title="VideoStream with transforms",
    sidebar=[component.settings],
    main=[component],
).servable()

# panel convert script2.py --to pyodide-worker --out pyodide --requirements requirements.txt
# panel serve script2.py --autoreload --port 5007
