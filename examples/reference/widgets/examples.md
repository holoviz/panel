```python
import panel as pn

pn.extension()
```

## Basic Usage

You can create an `Examples` widget to pick examples for a single target:

```python
widget = pn.widgets.TextInput(name="Selection")
examples = pn.widgets.Examples("Hello", "World", targets=widget)
pn.Column(examples, widget).servable()
```

The `Examples` widget is *list like*, i.e. you can work with it as a list:

```python
pn.Row(examples[1], examples[0]).servable()
```

To gain more control over the look of the examples you can provide `Example` values:

```python
from panel.widgets import Example

widget = pn.widgets.TextInput(name="Selection")
examples = pn.widgets.Examples(Example("Hello", "HELLO", button_kwargs={"button_style": "outline"}), Example("Hello World", "", "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLZf31OpU0zqzpDS-IwNBp7lF1eejh9YJHHA&s"), targets=widget)
pn.Column(examples, widget).servable()
```

## Multiple Targets

You can create an `Examples` widget to pick examples for multiple targets:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

examples = pn.widgets.Examples(("Stanford", "https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "TEXT INPUT"), ("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), targets=[text_input, audio_output, update_name], name="🎵 Audio Examples")
pn.FlexBox(examples, text_input, audio_output).servable()
```

Please note targets can be widgets, panes and functions.

If your want to see the values as well as the buttons you can provide a `layout`:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

examples = pn.widgets.Examples(("Stanford", "https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "TEXT INPUT"), ("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), targets=[text_input, audio_output, update_name], name="🎵 Audio Examples", layout=pn.Row, sizing_mode="fixed", width=600)
pn.Column(examples, text_input, audio_output).servable()
```

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

samples = [pn.widgets.Example((f"Beat Boxing {index}", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), name=f"Beat Boxing {index}", targets=[text_input, audio_output, update_name], layout=None) for index in range(0,100)]
# Todo: support height and scroll parameters
examples = pn.widgets.Examples(*samples, targets=[text_input, audio_output, update_name], name="🎵 Audio Examples", layout=pn.Row, height=400, sizing_mode="stretch_width")
pn.Column(examples, pn.Row(text_input, audio_output, margin=(50,5,10,5))).servable()
```

FIGURE OUT WHY TOP MARGIN OF 50 IS NEEDED.
