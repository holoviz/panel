```python
import panel as pn

pn.extension()
```

The `Example` widget enables you to present a single example to the user to pick. When clicked
one or more `targets` will be updated or called.

#### Parameters

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`value`** (str | iterable[Any]): The example value. Either a single value or an iterable of values to assign to a single or an iterable of `targets` when updated or triggered.
* **`name`** (str): An Optional name. Will be used as the Button label if not "". Default is "".
* **`thumbnail`** (str | Path): An Optional thumbnail image. A local file will be embedded as a *data url*. Default is "".
* **`targets`** (object | list[object] | None): An Optional object or list of objects. The individual object can be a class with a `.value` or `.object` attribute - for example a widget or pane. Can also be a callable taking a single argument. Will be updated or called when the `value` is updated or triggered. Default is None.

##### Display

* **`layout`** (ListPanel or None): An optional list like layout. If None the `Example` will be layout as a Button. If `Row` as a row with a Button and the value items. Default is None.
* **`button_kwargs`** (dict): An optional dictionary of `Button` keyword arguments like `button_type` or `height`.

## Basic Usage

You can create an `Example` to pick examples for a single target:

```python
widget = pn.widgets.TextInput(name="Selection")
example = pn.widgets.Example("Hello", targets=widget)
pn.Column(example, widget).servable()
```

You can give the `Example` a specific `name`:

```python
widget = pn.widgets.TextInput(name="Selection")
example = pn.widgets.Example("World", name="Hello", targets=widget)
pn.Column(example, widget).servable()
```

Or a `thumbnail`:

```python
widget = pn.widgets.TextInput(name="Selection")
example = pn.widgets.Example("Hello World", thumbnail="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLZf31OpU0zqzpDS-IwNBp7lF1eejh9YJHHA&s", targets=widget)
pn.Column(example, widget).servable()
```

You can also provide provide your own custom `button_kwargs`:

```python
widget = pn.widgets.TextInput(name="Selection")
example = pn.widgets.Example("Hello", targets=widget, button_kwargs=dict(button_type="primary", button_style="outline", height=50, width=50))
pn.Column(example, widget).servable()
```

## Multiple Targets

You can create an `Example` to pick examples for multiple targets:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

example = pn.widgets.Example(("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), targets=[text_input, audio_output, update_name], name="beatboxing.mp3")
pn.Column(example, pn.Row(text_input, audio_output)).servable()
```

You can change the `layout` to `Row` to see the `Example` values:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

example = pn.widgets.Example(("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), targets=[text_input, audio_output, update_name], name="beatboxing.mp3", layout=pn.Row)
pn.Column(example, pn.Row(text_input, audio_output)).servable()
```

## Multiple Examples

You can create many examples:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

examples = [pn.widgets.Example((f"Beat Boxing {index}", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), name=f"Beat Boxing {index}", targets=[text_input, audio_output, update_name], layout=None) for index in range(0,100)]
pn.Column(pn.Column(pn.FlexBox(*examples), height=250, scroll=True), pn.Row(text_input, audio_output),).servable()
```

For efficient columnar layout of `Example` rows use the `Feed`:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

examples = [pn.widgets.Example((f"Beat Boxing {index}", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), name=f"Beat Boxing {index}", targets=[text_input, audio_output, update_name], layout=pn.Row) for index in range(0,100)]
pn.Column(pn.Feed(*examples, height=250, scroll=True, load_buffer=200), pn.Row(text_input, audio_output),).servable()
```
