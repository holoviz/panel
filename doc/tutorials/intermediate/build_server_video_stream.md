# Build a Server Side Video Camera Application

Welcome to our tutorial on building a **server-side video camera application** using HoloViz Panel! In this fun and engaging guide, we'll walk you through the process of setting up a video stream from a camera connected to a server, not the user's machine. This approach uses Python's threading to handle real-time video processing without freezing the user interface.

<video muted controls loop poster="../../_static/images/serverside-video.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/serverside-video.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

:::{dropdown} Code

`server_video_stream.py`

```python
import threading
import time

import cv2 as cv
import param

from PIL import Image

import panel as pn

class CannotOpenCamera(Exception):
    """Exception raised if the camera cannot be opened."""

class CannotReadCamera(Exception):
    """Exception raised if the camera cannot be read."""


class ServerVideoStream(pn.viewable.Viewer):
    value = param.Parameter(doc="The current snapshot as a Pillow Image")
    paused = param.Boolean(default=False, doc="Whether the video stream is paused")
    fps = param.Number(10, doc="Frames per second", inclusive_bounds=(0, None))
    camera_index = param.Integer(0, doc="The index of the active camera")

    def __init__(self, **params):
        super().__init__(**params)

        self._cameras = {}

        self._stop_thread = False
        self._thread = threading.Thread(target=self._take_images)
        self._thread.daemon = True

    def start(self, camera_indices=None):
        if camera_indices:
            for index in camera_indices:
                self.get_camera(index)

        if not self._thread.is_alive():
            self._thread.start()

    def get_camera(self, index):
        if index in self._cameras:
            return self._cameras[index]

        cap = cv.VideoCapture(index)

        if not cap.isOpened():
            raise CannotOpenCamera(f"Cannot open the camera {index}")

        self._cameras[index] = cap
        return cap

    @staticmethod
    def _cv2_to_pil(bgr_image):
        rgb_image = cv.cvtColor(bgr_image, cv.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        return image

    def _take_image(self):
        camera = self.get_camera(self.camera_index)
        ret, frame = camera.read()
        if not ret:
            raise CannotReadCamera("Ensure the camera exists and is not in use by other processes.")
        else:
            self.value = self._cv2_to_pil(frame)

    def _take_images(self):
        while not self._stop_thread:
            start_time = time.time()
            if not self.paused:
                try:
                    self._take_image()
                except Exception as ex:
                    print("Error: Could not capture image.")
                    print(ex)

            if self.fps > 0:
                interval = 1 / self.fps
                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                time.sleep(sleep_time)

    def __del__(self):
        self._stop_thread = True
        if self._thread.is_alive():
            self._thread.join()
        for camera in self._cameras.values():
            camera.release()
        cv.destroyAllWindows()

    def __panel__(self):
        settings = pn.Column(
            self.param.paused,
            self.param.fps,
            self.param.camera_index,
            width=300,
        )
        image = pn.pane.Image(self.param.value, sizing_mode="stretch_both")
        return pn.Row(settings, image)


server_video_stream = ServerVideoStream()
server_video_stream.start()
```

`app.py`

```python
import panel as pn
from server_video_stream import server_video_stream

pn.extension()

server_video_stream.servable()
```

:::

Let's dive into the code and see how it all comes together.

## Install the Dependencies

To run the application, you'll need several packages:

- **OpenCV** (`opencv`): A library for computer vision tasks, here used to interface with the camera.
- **Panel** (`panel`): A high-level app and dashboarding solution for Python, used to create the web interface.
- **Pillow** (`pillow`): An imaging library, used here to convert images from OpenCV format to a format suitable for web display.

You can install these using conda or pip:

::::{tab-set}

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge opencv panel pillow watchfiles
```

:::

:::{tab-item} pip
:sync: pip

``` bash
pip install opencv-python panel pillow watchfiles
```

:::

::::

## Build the App

### File Breakdown

This project consists of two Python files:

- `server_video_stream.py` - Contains the reusable `ServerVideoStream` component.
- `app.py` - A simple script that utilizes the `server_video_stream` component.

### Breakdown of `server_video_stream.py`

#### Importing Libraries and Handling Exceptions

```python
import threading
import time

import cv2 as cv
import param

from PIL import Image

import panel as pn

class CannotOpenCamera(Exception):
    """Exception raised if the camera cannot be opened."""

class CannotReadCamera(Exception):
    """Exception raised if the camera cannot be read."""
```

We begin by importing the necessary libraries:

- **threading**: For running background tasks that do not block the main program.
- **time**: To manage frame rates and delays.
- **cv2**: The [OpenCV](https://docs.opencv.org/4.x/) library for capturing and processing video frames.
- **param**: A component of the HoloViz ecosystem for declaring parameters.
- **Image from PIL**: To convert images from OpenCV's format to a web-friendly format.
- **panel**: The Panel library for creating web interfaces.

We also define several custom exceptions to manage specific errors related to camera operations.

#### Defining the `ServerVideoStream` Class

```python
class ServerVideoStream(pn.viewable.Viewer):
    value = param.Parameter(doc="The current snapshot as a Pillow Image")
    paused = param.Boolean(default=False, doc="Whether the video stream is paused")
    fps = param.Number(10, doc="Frames per second", inclusive_bounds=(0, None))
    camera_index = param.Integer(0, doc="The index of the active camera")
```

The `ServerVideoStream` class extends `pn.viewable.Viewer`, enabling its display in a Panel app. It includes parameters to control the stream:

- **value**: Holds the current video frame.
- **paused**: A toggle to pause or resume the video capture.
- **fps**: Determines the frame rate of the video stream.
- **camera_index**: Specifies which camera to use if multiple are available.

#### Initializing and Managing Cameras

```python
    def __init__(self, **params):
        super().__init__(**params)

        self._cameras = {}

        self._stop_thread = False
        self._thread = threading.Thread(target=self._take_images)
        self._thread.daemon = True

    def start(self, camera_indices):
        if camera_indices:
            for index in camera_indices:
                self.get_camera(index)

        if not self._thread.is_alive():
            self._thread.start()
```

The constructor initializes a thread for capturing images and managing the stream. The `start` method activates the cameras and starts the thread if it isn't already running.

#### Capturing and Displaying Images

```python
    def get_camera(self, index):
        if index in self._cameras:
            return self._cameras[index]

        cap = cv.VideoCapture(index)
        if not cap.isOpened():
            raise CannotOpenCamera(f"Cannot open the camera {index}")

        self._cameras[index] = cap
        return cap

    @staticmethod
    def _cv2_to_pil(bgr_image):
        rgb_image = cv.cvtColor(bgr_image, cv.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_image)
        return image

    def _take_image(self):
        camera = self.get_camera(self.camera_index)
        ret, frame = camera.read()
        if not ret:
            raise CannotReadCamera("Ensure the camera exists and is not in use by other processes.")
        else:
            self.value = self._cv2_to_pil(frame)

    def _take_images(self):
        while not self._stop_thread:
            start_time = time.time()
            if not self.paused:
                try:
                    self._take_image()
                except Exception as ex:
                    print("Error: Could not capture image.")
                    print(ex)

            if self.fps > 0:
                interval = 1 / self.fps
                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                time.sleep(sleep_time)

    def __del__(self):
        self._stop_thread = True
        if self._thread.is_alive():
            self._thread.join()
        for camera in self._cameras.values():
            camera.release()
        cv.destroyAllWindows()
```

The `_take_images` method runs in a loop within a separate thread, capturing images at the specified fps unless paused. This setup ensures the app remains responsive by not blocking the main thread.

#### Display Setup

```python
    def __panel__(self):
        settings = pn.Column(
            self.param.paused,
            self.param.fps,
            self.param.camera_index,
            width=300,
        )
        image = pn.pane.Image(self.param.value, sizing_mode="stretch_both")
        return pn.Row(settings, image)
```

The `__panel__` method defines how the class is rendered in a web page. It creates a user interface with controls for the camera settings and displays the current video frame.

#### Sharing the Video Stream

```python
server_video_stream = ServerVideoStream()
server_video_stream.start()
```

To share the video camera between all user sessions, we utilize a single instance.

The `server_video_stream` is now ready for use in either a single or multi-page application. You can bind to its value or include the component in a layout.

### `app.py` - Making It Servable

```python
import panel as pn
from server_video_stream import server_video_stream

pn.extension()

server_video_stream.servable()
```

This script initializes the Panel extension and makes the `server_video_stream` instance available as a web app.

Try serving the app with

```bash
panel serve app.py
```

It should look like:

<video muted controls loop poster="../../_static/images/serverside-video.png" style="max-height: 400px; max-width: 100%;">
    <source src="https://assets.holoviz.org/panel/tutorials/serverside-video.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## References

### How-To Guides

- [Manual Threading](../../how_to/concurrency/manual_threading.md)
