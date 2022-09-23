# Linking objects in Panel

In the [Param user guide](Param.md), we have seen how Parameterized classes can be used to automatically generate a graphical user interface for Python code without any additional effort. If you need full control over how your GUI is set up, you can instead manually define widgets linking directly to other objects using either Python or JavaScript (JS) callbacks. Python callbacks are simple for Python users to write and can directly access Python data structures, while JS callbacks can directly manipulate the displayed HTML document and allow setting up dynamic behavior even for exported HTML files (with no Python process running).

Here we will show how to link parameters of Panel objects, typically from widgets to other objects. To do this, we will introduce three API calls:

* ``obj.link``: convenient high-level API to link objects via Python calls
* ``obj.param.watch``: powerful but lower-level Python API provided by [param](https://param.pyviz.org)
* ``obj.jslink``: high-level API to link objects via JS code
* ``obj.jscallback``: a lower-level API to define arbitrary Javascript callbacks

At the end of this notebook, we will then show how to use these APIs to set up links between widgets and plots that work even in exported HTML files where the Python process is no longer available.


```{pyodide}
import numpy as np
import panel as pn
pn.extension()
```

## Python links using the ``link`` method

To start, let's see how a ``TextInput`` widget and a ``Markdown`` pane normally behave:


```{pyodide}
pn.Row(pn.widgets.TextInput(value="Editable text"), pn.pane.Markdown('Some markdown'))
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


## Python links using the ``watch`` method

The ``link`` method used above provides a high-level API to link to parameters, which is adequate in most cases. If we need more control, we can fall back to the underlying ``param.watch`` method, which is what Panel uses internally to make all reactive features work. The main differences are that ``watch`` 1) does not assume you are linking two objects, providing more control over what you are watching, 2) allows batched callbacks when multiple parameters change at once, and 3) allows you to specify that an event should be triggered every time the parameter is set (instead of the default of only when the parameter value actually changes). If you do not need this level of control, just skip to the [Linking objects in JS](#Linking-objects-in-JS) section below.

To demonstrate ``param.watch``, let us set up three different models: 1) a `Markdown` pane to display the possible options, 2) a ``Markdown`` pane to display the _selected_ options, and 3) a ``ToggleGroup`` widget that allows us to toggle between a number of options:

```{pyodide}
selections = pn.pane.Markdown(object='')
selected = pn.pane.Markdown(object='')
toggle = pn.widgets.ToggleGroup(options=['A', 'B'])
```

### Defining a callback

Next we define a callback that can handle multiple parameter changes at once and uses the ``Event``'s ``name`` to figure out how to process the event. In this case it updates either the ``selections`` or the ``selected`` pane depending on whether ToggleGroup ``options`` or ``value`` changed:


```{pyodide}
def callback(*events):
    print(events)
    for event in events:
        if event.name == 'options':
            selections.object = 'Possible options: %s' % ', '.join(event.new)
        elif event.name == 'value':
            selected.object = 'Selected: %s' % ','.join(event.new)
```

### Event objects

Before going any further let us discover what these ``Event`` objects are. An ``Event`` is used to signal the change in a parameter value. Event objects provide a number of useful attributes that provides additional information about the event:

* **``name``**: The name of the parameter that has changed
* **``new``**: The new value of the parameter
* **``old``**: The old value of the parameter before the event was triggered
* **``type``**: The type of event ('triggered', 'changed', or 'set')
* **``what``**: Describes what about the parameter changed (usually the value but other parameter attributes can also change)
* **``obj``**: The Parameterized instance that holds the parameter
* **``cls``**: The Parameterized class that holds the parameter

### Registering a watcher

Now that we know how to define a callback and make use of ``Event`` attributes, it is time to register the callback. The ``obj.param.watch`` method lets us supply the callback along with the parameters we want to watch. Additionally we can declare whether the events should only be triggered when the parameter value changes, or every time the parameter is set:


```{pyodide}
watcher = toggle.param.watch(callback, ['options', 'value'], onlychanged=False)
```

Now let us display the widget alongside the ``Markdown`` panes that reflect the current state of the widget:


```{pyodide}
pn.Row(pn.Column(toggle, width=200, height=50), selections, pn.Spacer(width=50, height=50), selected)
```

To initialize the `selections` and `selected` we can explicitly ``trigger`` options and value events:


```{pyodide}
toggle.param.trigger('options', 'value')
```

We can also override the initial parameters using the ``set_param`` method:


```{pyodide}
options = ['A','B','C','D']
toggle.param.set_param(options=dict(zip(options,options)), value=['D'])
```

Using `set_param` allows us to batch two separate changes (the options and the value) together, which you can see from the ``print`` output resulted into a single invocation of the callback.  You could instead have set them separately using the usual parameter-setting syntax `toggle.value=['D']; toggle.options=dict(zip(options,options))`, but batching them can be much more efficient for a non-trivial callback like a database query or a complex plot that needs updating.

Now that the widgets are visible, you can toggle the option values and see the selected pane update in response via the callback (if Python is running).

### Unlinking

If for whatever reason we want to stop watching parameter changes we can unsubscribe by passing our ``watcher`` (returned in the ``watch`` call above) to the ``unwatch`` method:


```{pyodide}
#toggle.param.unwatch(watcher)
```

## Linking objects in JS

Linking objects in Python is often very convenient, because it allows writing code entirely in Python. However, it also requires a live Python kernel. If instead we want a static example (e.g. on a simple website or in an email) to have custom interactivity, or we simply want to avoid the overhead of having to call back into Python, we can define links in JavaScript.

### Linking Panel components

To begin with let us see how we can express simple links between standard Panel components before digging into some more specific and complex examples.

#### Linking model properties

Let us start by rehashing the example from above, linking the ``value`` of the ``TextInput`` widget to the ``object`` property of the ``Markdown`` pane:


```{pyodide}
markdown = pn.pane.Markdown('Markdown display')
text_input = pn.widgets.TextInput(value=markdown.object)

link = text_input.jslink(markdown, value='object')

pn.Row(text_input, markdown)
```

As you can see the signature is identical to the ``link`` example above, but here Panel translates the specification into a JS code snippet which syncs the properties on the underlying Bokeh properties. But now if you edit the widget and press Return, the Markdown display will automatically update even in a static HTML web page.

#### Linking bi-directionally

When you want the source and target to be linked bi-directionally, i.e. a change in one will automatically trigger a change in the other you can simply set the `bidirectional` argument:


```{pyodide}
t1 = pn.widgets.TextInput()
t2 = pn.widgets.TextInput()

t1.jslink(t2, value='value', bidirectional=True)

pn.Row(t1, t2)
```

#### Linking using custom JS code

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
text_input.value="Markdown display"
```

#### Open URL

As an example of using `jslink`, here we open a URL from the ``TextInput`` widget value. A new browser tab will open with the provided URL:


```{pyodide}
button = pn.widgets.Button(name='Open URL', button_type = 'primary')
url = pn.widgets.TextInput(name='URL', value = 'https://pyviz.org/')
button.js_on_click(args={'target': url}, code='window.open(target.value)')
pn.Row(url, button)
```

## Defining Javascript callbacks

Sometimes defining a simple link between to objects is not sufficient, e.g. when there are a number of objects involved. In these cases it is helpful to be able to define arbitrary Javascript callbacks. A very simple example is a very basic calculator which allows multiplying or adding two values, in this case we have two widgets to input numbers, a selector to pick the operation, a display for the result and a button.

To implement this we define a `jscallback`, which is triggered when the `Button.clicks` property changes and provide a number of `args` allowing us to access the values of the various widgets:


```{pyodide}
value1 =   pn.widgets.Spinner(value=0, width=75)
operator = pn.widgets.Select(value='*', options=['*', '+'], width=50, align='center')
value2 =   pn.widgets.Spinner(value=0, width=75)
button =   pn.widgets.Button(name='=', width=50)
result =   pn.widgets.StaticText(value='0', width=50, align='center')

button.jscallback(clicks="""
if (op.value == '*')
  result.text = (v1.value * v2.value).toString()
else
  result.text = (v1.value + v2.value).toString()
""", args={'op': operator, 'result': result, 'v1': value1, 'v2': value2})

pn.Row(value1, operator, value2, button, result)
```

## Linking Plots

The above examples link widgets to simple static panes, but links are probably most useful when combined with dynamic objects like plots.

### Bokeh

The ``jslink`` API trivially allows us to link a parameter on a Panel widget to a Bokeh plot property. Here we create a Bokeh Figure with a simple sine curve. The ``jslink`` method allows us to pass any Bokeh model held by the Figure as the ``target``, then link the widget value to some property on it. E.g. here we link a ``FloatSlider`` value to the ``line_width`` of the ``Line`` glyph:


```{pyodide}
from bokeh.plotting import figure

p = figure(width=300, height=300)
xs = np.linspace(0, 10)
r = p.line(xs, np.sin(xs))

width_slider = pn.widgets.FloatSlider(name='Line Width', start=0.1, end=10)
width_slider.jslink(r.glyph, value='line_width')

pn.Column(width_slider, p)
```

### HoloViews

Bokeh models allow us to directly access the underlying models and properties, but this access is more indirect when working with HoloViews objects. HoloViews makes various models available directly in the namespace so that they can be accessed for linking:

* **``cds``**: The bokeh ``ColumnDataSource`` model which holds the data used to render the plot
* **``glyph``**: The bokeh ``Glyph`` defining the style of the element
* **``glyph_renderer``**: The Bokeh ``GlyphRenderer`` responsible for rendering the element
* **``plot``**: The bokeh ``Figure``
* **``xaxis``/``yaxis``**: The Axis models of the plot
* **``x_range``/``y_range``**: The x/y-axis ``Range1d`` models defining the axis ranges

All these are made available in the JS code's namespace if we decide to provide a JS code snippet, but can also be referenced in the property mapping. We can map the widget value to a property on the ``glyph`` by providing a specification separated by periods. E.g. in this case we can map the value to the ``glyph.size``:


```{pyodide}
import holoviews as hv
import holoviews.plotting.bokeh

colors = ["black", "red", "blue", "green", "gray"]

size_widget = pn.widgets.FloatSlider(value=8, start=3, end=20, name='Size')
color_widget = pn.widgets.Select(name='Color', options=colors, value='black')

points = hv.Points(np.random.rand(10, 2)).options(padding=0.1, line_color='black')

size_widget.jslink(points, value='glyph.size')
color_widget.jslink(points, value='glyph.fill_color')

pn.Row(points, pn.Column(size_widget, color_widget))
```

Of course, if you need to transform between the displayed widget value and the value to be used on the underlying Bokeh property, you can add custom JS code as shown in [the previous section](#Linking-using-custom-JS-code). Together these linking options should allow you to express whatever interactions you wish between your Panel objects.
