```python
import panel as pn

pn.extension()
```

## Basic Usage

You can create an `ExamplePicker` to pick examples for a single target:

```python
widget = pn.widgets.TextInput(name="Selection")
example_picker = pn.widgets.ExamplePicker("Hello", "World", targets=widget)
pn.FlexBox(example_picker, widget).servable()
```

## Multiple Targets

You can create an `ExamplePicker` to pick examples for multiple targets:

```python
text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

example_picker = pn.widgets.ExamplePicker(("Stanford", "https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "TEXT INPUT"), ("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"), targets=[text_input, audio_output, update_name], name="🎵 Audio Examples")
pn.FlexBox(example_picker, text_input, audio_output).servable()
```

Please note targets can be widgets, panes and functions.

You can further customize the buttons using the `Example` class

```python
from panel.widgets.example_picker import Example

text_input = pn.widgets.TextInput(name="Text Input")
audio_output = pn.pane.Audio(name="Audio Output")
def update_name(name, text_input=text_input):
    text_input.name=name

targets = [text_input, audio_output, update_name]
examples = [
    Example(name="pno-cs.mp3", value=("Stanford", "https://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", "TEXT INPUT")),
    Example(name="beatboxing.mp3", value=("Beat Boxing", "https://assets.holoviz.org/panel/samples/beatboxing.mp3", "text input"))
]

example_picker = pn.widgets.ExamplePicker(*examples, targets=targets, name="🎵 Audio Examples")
pn.FlexBox(example_picker, text_input, audio_output).servable()
```
