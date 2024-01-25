# Link Two Objects in Javascript

This guide addresses how to link parameters of two objects in Javascript.

---

Linking objects in Python is often very convenient because it allows writing code entirely in Python. However, it also requires a live Python kernel. If instead we want a static example (e.g. on a simple website or in an email) to have custom interactivity, or we simply want to avoid the overhead of having to call back into Python, we can define links in JavaScript.

## Link model properties

Let us start by linking the ``value`` of the ``TextInput`` widget to the ``object`` property of a ``Markdown`` pane:

```{pyodide}
import panel as pn

pn.extension()

markdown = pn.pane.Markdown('Markdown display')
text_input = pn.widgets.TextInput(value=markdown.object)

link = text_input.jslink(markdown, value='object')

pn.Row(text_input, markdown)
```

As you can see, Panel translates the specification into a JS code snippet which syncs the properties on the underlying Bokeh properties. But now if you edit the widget and press Return, the Markdown display will automatically update even in a static HTML web page.

## Link bi-directionally

When you want the source and target to be linked bi-directionally, i.e. a change in one will automatically trigger a change in the other you can simply set the `bidirectional` argument:


```{pyodide}
t1 = pn.widgets.TextInput()
t2 = pn.widgets.TextInput()

t1.jslink(t2, value='value', bidirectional=True)

pn.Row(t1, t2)
```

## Link using custom JS code

Since everything happens in JS for a `jslink`, we can't provide a Python callback. Instead, we can define a JS code snippet, which is executed when a property changes. E.g. we can define a little code snippet which adds HTML bold tags (``<b>``) around the text before setting it on the target. The code argument should map from the parameter/property on the source object to the JS code snippet to execute:


```{pyodide}
markdown = pn.pane.Markdown("<b>Markdown display</b>", width=400)
text_input = pn.widgets.TextInput(value="Markdown display")

code = '''
    target.text = '<b>' + source.value + '</b>'
'''
link = text_input.jslink(markdown, code={'value': code})

pn.Row(text_input, markdown)
```

Here ``source`` and ``target`` are made available in the JavaScript namespace, allowing us to arbitrarily modify the models in response to property change events. Note however that the underlying Bokeh model property names may differ slightly from the naming of the parameters on Panel objects, e.g. the 'object' parameter on the Markdown pane translates to the 'text' property on the Bokeh model used to render the ``Markdown``.

Of course, you can still update the value from Python, and it will automatically update the linked markdown:


```{pyodide}
text_input.value = "Markdown display"
```

## Responding to click events

To respond to click events, we'll demonstrate an example of using `js_on_click`. This example will open a URL from the ``TextInput`` widget value in a new browser tab:

```{pyodide}
button = pn.widgets.Button(name='Open URL', button_type = 'primary')
url = pn.widgets.TextInput(name='URL', value = 'https://holoviz.org/')
button.js_on_click(args={'target': url}, code='window.open(target.value)')
pn.Row(url, button)
```

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
- The [How to > Link Plot Parameters in Javascript](./link_plots.md) guide addresses how to link Bokeh and HoloViews plot parameters in Javascript.
