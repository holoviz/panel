# Custom Widgets

In this guide we will show you how to efficiently implement custom widgets using `JSComponent`, `ReactComponent` and `PreactComponent` to get input from the user.

## Image Button

This example we will show you to create an `ImageButton`.

```{pyodide}
import panel as pn
import param

from panel.custom import JSComponent

pn.extension()

class ImageButton(JSComponent):

    clicks = param.Integer(default=0)
    image = param.String()

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

button = ImageButton(
    image="https://raw.githubusercontent.com/holoviz/holoviz/25ac96dbc09f789612eb8e03a5deb36c5cd74393/examples/assets/panel.png",
    styles={"border": "2px solid lightgray"},
    width=400, height=200
)
pn.Column(button, button.param.clicks,).servable()
```

If you don't want the *button* styling, you can change the `<button>` tag to a `<div>` tag.

The `ImageButton` now works as any other widget. Lets try the `.from_param` method to create a `ImageButton` from a `param` class.

```{pyodide}
class MyClass(param.Parameterized):
    value = param.Event()

    clicks = param.Integer(default=0)

    @param.depends("value", watch=True)
    def _handle_value(self):
        if self.value:
            self.clicks+=1

my_instance=MyClass()
button2=ImageButton.from_param(my_instance.param.value)
pn.Column(button2, my_instance.param.clicks).servable()
```

When you click the image button you should see the number of clicks increase.
