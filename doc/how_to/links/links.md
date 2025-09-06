# Create High-Level Python Links with `.link`

This guide addresses how to use the convenient, high-level `.link` API to link parameters in Python.

---

To start, let's see how a ``TextInput`` widget and a ``Markdown`` pane normally behave:

```{pyodide}
import panel as pn

pn.extension()

pn.Row(
    pn.widgets.TextInput(value="Editable text"),
    pn.pane.Markdown('Some markdown')
)
```

These two Panel objects are entirely independent; text can be entered into the input area and separately the Markdown pane will display its argument.

What if we wanted connected input and output displays?  One option when you expect to have a live Python process available is to use the ``link`` method on Widgets to link its parameters to some other Panel object. In the simplest case we simply provide the ``target`` object and define the mapping between the source and target parameters as the keywords. In this case, we map the ``value`` parameter on the ``TextInput`` widget to the ``object`` parameter on the ``Markdown`` pane:

```{pyodide}
markdown = pn.pane.Markdown("Some text")
text_input = pn.widgets.TextInput(value=markdown.object)

text_input.link(markdown, value='object')

pn.Row(text_input, markdown)
```

Now, if Python is running and you type something in the box above and press Return, the corresponding Markdown pane should update to match.  And if you use Python to directly manipulate the value of the text input (e.g. by editing the following cell to have new text in it and then executing it), then the Markdown should also update to match:

```{pyodide}
text_input.value = 'Some text'
```

For more complex mappings between the widget value and the target parameter, we can define an arbitrary transformation as a Python callback:

```{pyodide}
m = pn.pane.Markdown("")
t = pn.widgets.TextInput()

def callback(target, event):
    target.object = event.new.upper() + '!!!'

t.link(m, callbacks={'value': callback})
t.value="Some text"

pn.Row(t, m)
```

Note that here we explicitly set `t.value` before displaying the panel to trigger the linked Markdown pane to update to match the text widget; callbacks are not otherwise triggered when the links are first set up.

---

## Related Resources
- See the [Explanation > APIs](../../explanation/api/index) for context on this and other Panel APIs
