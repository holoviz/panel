import io

import numpy as np
import PIL

from skimage import data
from skimage.draw import rectangle
from skimage.feature import Cascade
import panel as pn

pn.extension()

# Load the trained file from the module root.
trained_file = data.lbp_frontal_face_cascade_filename()

# Initialize the detector cascade.
detector = Cascade(trained_file)

image = data.astronaut()

def to_buffer(image: np.ndarray):
    # image = (image * 255).astype(np.uint8)
    pil_img = PIL.Image.fromarray(image)
    buff = io.BytesIO()
    pil_img.save(buff, format="JPEG")
    return buff


buffer = to_buffer(image)

pn.pane.JPG(buffer).servable()
