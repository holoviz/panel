# Dev Experience

```{pyodide}
import time

import param
import panel as pn

pn.extension()
```

The best practices described on this page serve as a checklist of items to keep in mind as you are developing your application. They include items we see users frequently get confused about or things that are easily missed but can make a big difference to the user experience of your application(s).

:::{note}
- Good: recommended, works.
- Okay: works (with intended behavior), potentially inefficient.
- Bad: Deprecated (may or may not work), just don't do it.
- Wrong: Not intended behavior, won't really work.
:::

### Bind on reference value, not value

#### Good

Be sure to bind on `obj.param.{parameter}`, not just `{parameter}`.

```{pyodide}
def show_clicks(clicks):
    return f"Number of clicks: {clicks}"

button = pn.widgets.Button(name="Click me!")
clicks = pn.bind(show_clicks, button.param.clicks)
pn.Row(button, clicks)
```

#### Wrong

If only on `{parameter}`, it will not trigger an update on change.

```{pyodide}
def show_clicks(clicks):
    return f"Number of clicks: {clicks}"

button = pn.widgets.Button(name="Click me!")
clicks = pn.bind(show_clicks, button.clicks)  # not button.clicks!
pn.Row(button, clicks)
```

### Inherit from `pn.viewer.Viewer`

#### Good

Instead of inheriting from `param.Parameterized`, using `pn.viewable.Viewer` allows direct invocation of the class, resembling a native Panel object.

For example, it's possible to use `ExampleApp().servable()` instead of `ExampleApp().view().servable()`.

```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    ...

    def __panel__(self):
        return pn.template.FastListTemplate(
            main=[...],
            sidebar=[...],
        )

ExampleApp().servable();  # semi-colon to suppress output in notebook
```

#### Okay

This method works, but should be reserved for cases where there's no Panel output.

```{pyodide}
class ExampleApp(param.Parameterized):

    ...

    def view(self):
        return pn.template.FastListTemplate(
            main=[...],
            sidebar=[...],
        )

ExampleApp().view().servable();  # semi-colon to suppress output in notebook
```

### Build widgets from parameters

#### Good

To translate multiple parameters into widgets, use `pn.Param`.

```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    width = param.Integer(default=100, bounds=(1, 200), label="Width of box")
    height = param.Integer(default=100, bounds=(1, 250), label="Height of box")
    color = param.Color(default="red", label="Color of box")

    def __panel__(self):
        return pn.Column(
            pn.Param(self, widgets={"height": pn.widgets.IntInput}),
            pn.pane.HTML(
                width=self.param.width,
                height=self.param.height,
                styles={"background-color": self.param.color},
            ),
        )


ExampleApp()
```

#### Good

You can also use `from_param` to manually build each component.

```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    width = param.Integer(default=100, bounds=(1, 200), label="Width of box")
    height = param.Integer(default=100, bounds=(1, 250), label="Height of box")
    color = param.Color(default="red", label="Color of box")

    def __panel__(self):
        width_slider = pn.widgets.IntSlider.from_param(self.param.width)
        height_input = pn.widgets.IntInput.from_param(self.param.height)
        color_picker = pn.widgets.ColorPicker.from_param(self.param.color)
        return pn.Column(
            width_slider,
            height_input,
            color_picker,
            pn.pane.HTML(
                width=self.param.width,
                height=self.param.height,
                styles={"background-color": self.param.color},
            ),
        )


ExampleApp()
```

#### Bad

If you instantiate individually through `param`, it's not bidirectional.


```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    width = param.Integer(default=100, bounds=(1, 200), label="Width of box")
    height = param.Integer(default=100, bounds=(1, 250), label="Height of box")
    color = param.Color(default="red", label="Color of box")

    def __panel__(self):
        width_slider = pn.widgets.IntSlider(
            value=self.param.width,
            start=self.param["width"].bounds[0],
            end=self.param["width"].bounds[1],
            name=self.param["width"].label,
        )
        height_input = pn.widgets.IntInput(
            value=self.param.height,
            start=self.param["height"].bounds[0],
            end=self.param["height"].bounds[1],
            name=self.param["height"].label,
        )
        color_picker = pn.widgets.ColorPicker(
            value=self.param.color,
            name=self.param["color"].label,
            width=200,
        )
        return pn.Column(
            width_slider,
            height_input,
            color_picker,
            pn.pane.HTML(
                width=self.param.width,
                height=self.param.height,
                styles={"background-color": self.param.color},
            ),
        )


ExampleApp()
```

#### Bad

It's possible to `link` each widget to `self` with `bidirectional=True`, but certain keyword arguments, like `bounds`, cannot be linked easily.

```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    width = param.Integer(default=100, bounds=(1, 200), label="Width of box")
    height = param.Integer(default=100, bounds=(1, 250), label="Height of box")
    color = param.Color(default="red", label="Color of box")

    def __panel__(self):
        width_slider = pn.widgets.IntSlider()
        height_input = pn.widgets.IntInput()
        color_picker = pn.widgets.ColorPicker()

        width_slider.link(self, value="width", bidirectional=True)
        height_input.link(self, value="height", bidirectional=True)
        color_picker.link(self, value="color", bidirectional=True)

        return pn.Column(
            width_slider,
            height_input,
            color_picker,
            pn.pane.HTML(
                width=self.param.width,
                height=self.param.height,
                styles={"background-color": self.param.color},
            ),
        )


ExampleApp()
```

#### Wrong

Widgets should not be used as parameters since all instances of the class will share the widget class:

```{pyodide}
class ExampleApp(pn.viewable.Viewer):

    width = pn.widgets.IntSlider()
    height = pn.widgets.IntInput()
    color = pn.widgets.ColorPicker()
```

### Show templates in notebooks

#### Good

Templates, at the time of writing, are not able to be rendered properly in Jupyter notebooks.

To continue working with templates in notebooks, call `show` to pop up a new browser window.

```{pyodide}
template = pn.template.FastListTemplate(
    main=[...],
    sidebar=[...],
)

# template.show()  # commented out to disable opening a new browser tab in example
```

#### Okay

Alternatively, you can use a barebones notebook template like the one below.

```{pyodide}
class NotebookPlaceholderTemplate(pn.viewable.Viewer):
    main = param.List()
    sidebar = param.List()
    header = param.List()
    title = param.String()

    def __panel__(self):
        title = pn.pane.Markdown(f"# {self.title}", sizing_mode="stretch_width")
        # pastel blue
        header_row = pn.Row(
            title,
            *self.header,
            sizing_mode="stretch_width",
            styles={"background": "#e6f2ff"},
        )
        main_col = pn.WidgetBox(*self.main, sizing_mode="stretch_both")
        sidebar_col = pn.WidgetBox(
            *self.sidebar, width=300, sizing_mode="stretch_height"
        )
        return pn.Column(
            header_row,
            pn.Row(sidebar_col, main_col, sizing_mode="stretch_both"),
            sizing_mode="stretch_both",
            min_height=400,
        )

template = pn.template.FastListTemplate(
    main=[...],
    sidebar=[...],
)

template;
```

### Yield to show intermediate values

#### Good

Use a generator (yield) to provide incremental updates.

```{pyodide}
def increment_to_value(value):
    for i in range(value):
        time.sleep(0.1)
        yield i

slider = pn.widgets.IntSlider(start=1, end=10)
output = pn.bind(increment_to_value, slider.param.value_throttled)
pn.Row(slider, output)
```

### Watch side effects

#### Good

For functions that trigger side effects, i.e. do not return anything (or returns None), be sure to set `watch=True` on `pn.bind` or `pn.depends`.

```{pyodide}
def print_clicks(clicks):
    print(f"Number of clicks: {clicks}")

button = pn.widgets.Button(name="Click me!")
pn.bind(print_clicks, button.param.clicks, watch=True)
button
```

#### Good

For buttons, you can also use `on_click`.

```{pyodide}
def print_clicks(event):
    clicks = event.new
    print(f"Number of clicks: {clicks}")

button = pn.widgets.Button(name="Click me!", on_click=print_clicks)
button
```

#### Okay

For all other widgets, use `obj.param.watch()` for side effects.

```{pyodide}
def print_clicks(event):
    clicks = event.new
    print(f"Number of clicks: {clicks}")

button = pn.widgets.Button(name="Click me!")
button.param.watch(print_clicks, "clicks")
button
```

### Refreshing layout objects

#### Good

Updating the `objects` on a layout should be done via the methods on the layout itself:

```{pyodide}
def print_objects(event):
    print(f"Got new {[pane.object for pane in event.new]}")

col = pn.Column("a", "b")

col.param.watch(print_objects, 'objects')

col
```

```{pyodide}
col[:] = ["c", *col.objects[1:]]
```

#### Wrong

Modifying container `objects` by index will not trigger the callback.

```{pyodide}
def print_objects(event):
    print(f"Got new {event.new}")

col = pn.Column("a", "b")

col.param.watch(print_objects, "objects")

col
```

```{pyodide}
col.objects[0] = ["c"]  # does not trigger
```

### Good

However, you **can** modify the container by index using the APIs on the component itself.

```{pyodide}
def print_objects(event):
    print(f"Got new {[pane.object for pane in event.new]}")

col = pn.Column("a", "b")

col.param.watch(print_objects, "objects")

col
```

```{pyodide}
# col.objects[0] = 'Foo'  # no
col[0] = 'Foo'  # yes
```
