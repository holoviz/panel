# My App

```python
import panel as pn

pn.extension(template='fast')
```

This application provides a minimal example demonstrating how to write an app in a Markdown file.

```python
widget = pn.ui.TextInput(value='world')

def hello_world(text):
    return f'Hello {text}!'

pn.ui.Row(widget, pn.bind(hello_world, widget)).servable()
```
