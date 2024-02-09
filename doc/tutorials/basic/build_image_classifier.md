# Build an Image Classifier

In this tutorial, we will collaboratively build an *Image Classifier* that can detect wind turbines in images. As a team, we will support the following functionalities:

- Uploading an image file
- Using an example image file
- Viewing the image file
- Viewing the predicted result

We will be using a *random* classifier initially, but you can later replace it with your own custom classifier if you want.

:::{note}
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Create the App

Run the code below.

```{pyodide}
import random
from io import BytesIO
from time import sleep

import hvplot.pandas
import pandas as pd
import requests
from PIL import Image

import panel as pn

IMAGE_DIM = 350

pn.extension(design="material", sizing_mode="stretch_width")

## Transformations


@pn.cache
def get_pil_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


@pn.cache
def get_plot(label):
    data = pd.Series(label).sort_values()
    return data.hvplot.barh(title="Prediction", ylim=(0, 100)).opts(default_tools=[])


## Custom Components


def get_label_view(fn, image: Image):
    return get_plot(fn(image))


def get_image_button(url, image_pane):
    button = pn.widgets.Button(
        width=100,
        height=100,
        stylesheets=[
            f"button {{background-image: url({url});background-size: cover;}}"
        ],
    )
    pn.bind(handle_example_click, button, url, image_pane, watch=True)
    return button


## Event Handlers


def handle_example_click(event, url, image_pane):
    image_pane.object = get_pil_image(url)


def handle_file_upload(value, image_pane):
    file = BytesIO(value)
    image_pane.object = Image.open(file)


def image_classification_interface(fn, examples):

    ## State

    # The image_view holds the *application state*
    # The whole application is about updating or viewing it
    # Should it be defined at the top?
    image_view = pn.pane.Image(
        get_pil_image(examples[0]),
        height=IMAGE_DIM,
        width=IMAGE_DIM,
        fixed_aspect=False,
        margin=0,
    )

    label_view = pn.pane.JSON()

    ## Inputs

    file_input = pn.widgets.FileInput(
        accept=".png,.jpeg",
    )
    pn.bind(handle_file_upload, file_input, image_view, watch=True)
    file_input_component = pn.Column("### Upload Image", file_input)

    examples_input_component = pn.Column(
        "### Examples", pn.Row(*(get_image_button(url, image_view) for url in examples))
    )

    ## Views

    label_view = pn.Row(
        pn.panel(
            pn.bind(get_label_view, fn=fn, image=image_view.param.object),
            defer_load=True,
            loading_indicator=True,
            height=IMAGE_DIM,
            width=IMAGE_DIM,
        )
    )

    ## Layouts

    input_component = pn.Column(
        "# Input",
        image_view,
        file_input_component,
        examples_input_component,
        width=IMAGE_DIM,
        margin=10,
    )

    output_component = pn.Column(
        "# Output",
        label_view,
        width=IMAGE_DIM,
        margin=10,
    )
    return pn.FlexBox(input_component, output_component)


def predict(image: Image):
    # Replace with your own image classification model
    sleep(1.5)
    a = random.uniform(0, 100)
    b = random.uniform(0, 100 - a)
    c = 100 - a - b
    return {
        "Wind Turbine": a,
        "Solar Panel": b,
        "Battery Storage": c,
    }


EXAMPLES = [
    # Replace with your own examples
    "https://assets.holoviz.org/panel/tutorials/wind_turbine.png",
    "https://assets.holoviz.org/panel/tutorials/solar_panel.png",
    "https://assets.holoviz.org/panel/tutorials/battery_storage.png",
]

image_classification_interface(fn=predict, examples=EXAMPLES).servable()
```

Try to

- Click an example image
- Upload an `.png` or `.jpg` image file

## Recap

In this tutorial we have built an *Image Classifier* that can detect wind turbines. We will support

- Uploading an image file
- Using an example image file
- Viewing the image file
- Viewing the predicted result
