# Create Low-Level Python Links Using ``.watch``

This guide addresses how to use the low-level `.watch` API to trigger callbacks on parameters.

```{admonition} Prerequisites
1. The [How to > Create High-Level Python Links with '.link'](./links) guide demonstrates a high-level API to link to parameters, which is adequate in most cases.
```

---

If we need more control than what `.link` provides, we can fall back to the underlying `.watch` method. The main differences are that `.watch`:
1) does not assume you are linking two objects (providing more control over what you are watching)
2) allows batched callbacks when multiple parameters change at once
3) allows you to specify that an event should be triggered every time the parameter is set (instead of the default of only when the parameter value actually changes)

To demonstrate `.watch`, let us set up three different models:
1) `Markdown` pane to display the possible options
2) `Markdown` pane to display the _selected_ options
3) `ToggleGroup` widget that allows us to toggle between a number of options

```{pyodide}
import panel as pn

pn.extension()

selections = pn.pane.Markdown(object='')
selected = pn.pane.Markdown(object='')
toggle = pn.widgets.ToggleGroup(options=['A', 'B'])
```

## Defining a callback

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

## Event objects

Before going any further let us discover what these ``Event`` objects are. An ``Event`` is used to signal the change in a parameter value. Event objects provide a number of useful attributes that provides additional information about the event:

* **``name``**: The name of the parameter that has changed
* **``new``**: The new value of the parameter
* **``old``**: The old value of the parameter before the event was triggered
* **``type``**: The type of event ('triggered', 'changed', or 'set')
* **``what``**: Describes what about the parameter changed (usually the value but other parameter attributes can also change)
* **``obj``**: The Parameterized instance that holds the parameter
* **``cls``**: The Parameterized class that holds the parameter

## Registering a watcher

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

We can also override the initial parameters using the ``update`` method:

```{pyodide}
options = ['A','B','C','D']
toggle.param.update(options=dict(zip(options,options)), value=['D'])
```

Using `update` allows us to batch two separate changes (the options and the value) together, which you can see from the ``print`` output resulted into a single invocation of the callback.  You could instead have set them separately using the usual parameter-setting syntax `toggle.value=['D']; toggle.options=dict(zip(options,options))`, but batching them can be much more efficient for a non-trivial callback like a database query or a complex plot that needs updating.

Now that the widgets are visible, you can toggle the option values and see the selected pane update in response via the callback (if Python is running).

## Unlinking

If for whatever reason we want to stop watching parameter changes we can unsubscribe by passing our ``watcher`` (returned in the ``watch`` call above) to the ``unwatch`` method:

```python
toggle.param.unwatch(watcher)
```

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
