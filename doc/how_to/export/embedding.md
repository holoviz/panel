# Embedding state

This guide addresses how to embed app state for usage entirely within Javascript.

---

Panel generally relies on either the Jupyter kernel or a Bokeh Server to be running in the background to provide interactive behavior. However for simple apps with a limited amount of state it is also possible to `embed` all the widget state, allowing the app to be used entirely from within Javascript. To demonstrate this we will create a simple app which simply takes a slider value, multiplies it by 5 and then display the result.

```
slider = pn.widgets.IntSlider(start=0, end=10)

def callback(value):
    return '%d * 5 = %d' % (value, value*5)

row = pn.Row(slider, pn.bind(callback, slider))
```

If we displayed this the normal way it would call back into Python every time the value changed. However, the `.embed()` method will record the state of the app for the different widget configurations.

```
row.embed()
```

If you try the widget above you will note that it only has 3 different states, 0, 5 and 10. This is because by default embed will try to limit the number of options of non-discrete or semi-discrete widgets to at most three values. This can be controlled using the `max_opts` argument to the embed method or you can provide an explicit list of `states` to embed for each widget:

```
row.embed(states={slider: list(range(0, 12, 2))})
```

 The full set of options for the embed method include:

- **`max_states`**: The maximum number of states to embed

- **`max_opts`**: The maximum number of states for a single widget

- **`states`** (default={}): A dictionary specifying the widget values to embed for each widget

- **`json`** (default=True): Whether to export the data to json files

- **`save_path`** (default='./'): The path to save json files to

- **`load_path`** (default=None):  The path or URL the json files will be loaded from (same as ``save_path`` if not specified)

* **`progress`** (default=False): Whether to report progress

As you might imagine if there are multiple widgets there can quickly be a combinatorial explosion of states so by default the output is limited to about 1000 states. For larger apps the states can also be exported to json files, e.g. if you want to serve the app on a website specify the ``save_path`` to declare where it will be stored and the ``load_path`` to declare where the JS code running on the website will look for the files.

## Related Resources
