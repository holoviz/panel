# Create Custom Widgets using ESM Components

In this guide we will show you how to efficiently implement custom widgets using `JSComponent`, `ReactComponent` and `AnyWidgetComponent` to get input from the user.

## Image Button

This example we will show you to create an `ImageButton`.

::::{tab-set}

:::{tab-item} `JSComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import JSComponent
from panel.widgets import WidgetBase

pn.extension()

class ImageButton(JSComponent, WidgetBase):

    clicks = param.Integer(default=0)
    image = param.String()
    value = param.Event()

    _esm = """
export function render({ model }) {
    const button = document.createElement('button');
    button.id = 'button';
    button.className = 'pn-container center-content';

    const img = document.createElement('img');
    img.id = 'image';
    img.className = 'image-size';
    img.src = model.image;

    button.appendChild(img);

    button.addEventListener('click', () => {
        model.clicks += 1;
    });
    return button
}
"""

    _stylesheets = ["""
.pn-container {
    height: 100%;
    width: 100%;
}
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1em;
}
.image-size {
    width: 100%;
    max-height: 100%;
    object-fit: contain;
}
"""]

    @param.depends('clicks')
    def _trigger_value(self):
       self.param.trigger('value')

button = ImageButton(
    image="https://panel.holoviz.org/_static/logo_stacked.png",
    styles={"border": "2px solid lightgray"},
    width=400, height=200
)
pn.Column(button, button.param.clicks,).servable()
```
:::

:::{tab-item} `ReactComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import ReactComponent
from panel.widgets import WidgetBase

pn.extension()

class ImageButton(ReactComponent, WidgetBase):

    clicks = param.Integer(default=0)
    image = param.String()
    value = param.Event()

    _esm = """
export function render({ model }) {
    const [clicks, setClicks] = model.useState("clicks");
    const [image] = model.useState("image");

    return (
    <button onClick={e => setClicks(clicks+1)} className="pn-container center-content">
        <img src={image} className="image-size" src={ image }/>
    </button>
    )
}
"""

    _stylesheets = ["""
.pn-container {
    height: 100%;
    width: 100%;
}
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1em;
}
.image-size {
    width: 100%;
    max-height: 100%;
    object-fit: contain;
}
"""]

    @param.depends('clicks')
    def _trigger_value(self):
       self.param.trigger('value')

button = ImageButton(
    image="https://panel.holoviz.org/_static/logo_stacked.png",
    styles={"border": "2px solid lightgray"},
    width=400
)
pn.Column(button, button.param.clicks).servable()
```
:::

:::{tab-item} `AnyWidgetComponent`
```{pyodide}
import panel as pn
import param

from panel.custom import AnyWidgetComponent
from panel.widgets import WidgetBase

pn.extension()

class ImageButton(AnyWidgetComponent, WidgetBase):

    clicks = param.Integer(default=0)
    image = param.String()
    value = param.Event()

    _esm = """
function render({ model, el }) {
    const button = document.createElement('button');
    button.id = 'button';
    button.className = 'pn-container center-content';

    const img = document.createElement('img');
    img.id = 'image';
    img.className = 'image-size';
    img.src = model.get("image");

    button.appendChild(img);

    button.addEventListener('click', () => {
        model.set("clicks", model.get("clicks")+1);
        model.save_changes();
    });
    el.appendChild(button);
}
export default { render }
"""

    _stylesheets = ["""
.pn-container {
    height: 100%;
    width: 100%;
}
.center-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1em;
}
.image-size {
    width: 100%;
    max-height: 100%;
    object-fit: contain;
}
"""]

    @param.depends('clicks')
    def _trigger_value(self):
       self.param.trigger('value')

button = ImageButton(
    image="https://panel.holoviz.org/_static/logo_stacked.png",
    styles={"border": "2px solid lightgray"},
    width=400, height=200
)

pn.Column(button, button.param.clicks).servable()
```
:::

::::

If you don't want the *button* styling, you can change the `<button>` tag to a `<div>` tag.

The `ImageButton` now works as any other widget. Lets try the `.from_param` method to create an `ImageButton` from a `Parameter:

```{pyodide}
class MyClass(param.Parameterized):

    clicks = param.Integer(default=0)

    value = param.Event()

    @param.depends("value", watch=True)
    def _handle_value(self):
        if self.value:
            self.clicks += 1

my_instance = MyClass()
button2 = ImageButton.from_param(my_instance.param.value, image="https://panel.holoviz.org/_static/logo_stacked.png",)
pn.Column(button2, my_instance.param.clicks).servable()
```

When you click the image button you should see the number of clicks increase.
