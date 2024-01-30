# Build a Todo App

In this tutorial we will build an *Image Classifier* that can detect wind turbines in images. We will support

- Uploading an image file
- Using an example image file
- Viewing the image file
- Viewing the predicted result

We will be using a *random* classifier. But you can replace it with your own classifier if you want.

:::{note}
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Create the App

TODO

- Remove Design Reference
- More clearly define `image` and `label` state.
- Make interface more gradio compatible by minimizing surface area between inputs and outputs.
- Consider using another plotting library than hvplot. `hbar` has many issues and do not support transitions. Use Vizzu, ECharts or Plotly?

```{pyodide}
# Design Reference: https://github.com/pytholic/gradio-image-classificaiton/blob/main/resources/demo.png?raw=true
import panel as pn
from PIL import Image
import random
import pandas as pd
from time import sleep
import hvplot.pandas
import requests
from io import BytesIO

IMAGE_DIM = 350

pn.extension(design="material", sizing_mode="stretch_width")

## Transformations

@pn.cache
def get_pil_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

@pn.cache
def get_plot(label):
    # Its not possible to control xlabel and ylabel of hbar: https://github.com/holoviz/hvplot/issues/973
    # And why is the x limit called ylim?
    data = pd.Series(label).sort_values()
    return data.hvplot.barh(title="Prediction", ylim=(0,100)).opts(default_tools=[])

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
        pn.panel(pn.bind(get_label_view, fn=fn, image=image_view.param.object), defer_load=True, loading_indicator=True, height=IMAGE_DIM, width=IMAGE_DIM)
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
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Windmills_D1-D4_%28Thornton_Bank%29.jpg/220px-Windmills_D1-D4_%28Thornton_Bank%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Solar_cell.png/220px-Solar_cell.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Overhead_View_of_Tehachapi_Energy_Storage_Project%2C_Tehachapi%2C_CA.png/220px-Overhead_View_of_Tehachapi_Energy_Storage_Project%2C_Tehachapi%2C_CA.png",
]

image_classification_interface(fn=predict, examples=EXAMPLES).servable()
```

Try to

- Click an example image
- Upload an `.png` or `.jpg` image file

## Break it down

We will now break down the example together to get a better understanding of the code.

COMING UP

## Recap

In this tutorial we have built an *Image Classifier* that can detect wind turbines. We will support

- Uploading an image file
- Using an example image file
- Viewing the image file
- Viewing the predicted result

## Resources

COMING UP
