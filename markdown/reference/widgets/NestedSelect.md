# NestedSelect
---
```python
import panel as pn
pn.extension()
```

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (dict | callable): The options to select from. The options may be nested dictionaries, lists, or callables that return those types. If callables are used, the callables must accept `level` and `value` keyword arguments, where `level` is the level that updated and `value` is a dictionary of the current values, containing keys up to the level that was updated.
* **``value``** (dict): The value from all the Select widgets; the keys are the levels names. If no levels names are specified, the keys are the levels indices.
* **``layout``** (ListPanel | dict): The layout type of the widgets. If a dictionary, a "type" key can be provided, to specify the layout type of the widgets, and any additional keyword arguments will be used to instantiate the layout.
* **``levels``** (list): Either a list of strings or a list of dictionaries. If a list of strings, the strings are used as the names of the levels. If a list of dictionaries, each dictionary may have a "name" key, which is used as the name of the level, a "type" key, which is used as the type of widget, and any corresponding widget keyword arguments; otherwise, will inherit layoutable keyword arguments from the `NestedSelect` itself, e.g. width, height, and sizing_mode. Must be specified if options is callable. Must be specified if options is callable.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    levels=["Model", "Resolution", "Initialization"],
)
select
```

Like most other widgets, ``NestedSelect`` has a value parameter that can be accessed or set:

```python
select.value
```

A different `layout` type can be provided to the `NestedSelect` to change the layout of the widgets.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    levels=["Model", "Resolution", "Initialization"],
    layout=pn.Row
)
select
```

If a dict is provided, a "type" key can be provided, to specify the layout type of the widgets, and any additional keyword arguments will be used to instantiate the layout.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    levels=["Model", "Resolution", "Initialization"],
    layout={"type": pn.GridBox, "ncols": 2}
)
select
```

If ``levels`` names are not set, the value is keyed off the level index.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
)
select.value
```

You can also define the default value by providing a dict.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    value={"Model": "NAME", "Resolution": "12 km", "Initialization": "12Z"},
    levels=["Model", "Resolution", "Initialization"],
)
select
```

Not all keys of the value need to be specified, and the keys can be specified in any order.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    value={"Initialization": "12Z", "Resolution": "0.5 deg"},
    levels=["Model", "Resolution", "Initialization"],
)
select
```

An incomplete definition of options can also be used. The corresponding subsequent widgets will be hidden.

```python
select = pn.widgets.NestedSelect(
    options={
        "NAME": {},
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
    },
    levels=["Model", "Resolution", "Initialization"],
)
select
```

The value for the hidden widgets will be `None`.

```python
select.value = {"Model": "NAME"}
```

Alternatively, `options` can be a callable. Its nested levels too: e.g. `options={"Daily": list_options, "Monthly": list_options}`.

If callables are used, the callables must accept `level` and `value` keyword arguments, where `level` is the level that updated and `value` is a dictionary of the current values, containing keys up to the level that was updated.

Note, the callable can vary across `options`, and `levels` must be provided if any of the `options` is callable.

```python
def list_options(level, value):
    if level == "time_step":
        options = {"Daily": list_options, "Monthly": list_options}
    elif level == "level_type":
        options = {f"{value['time_step']}_upper": list_options, f"{value['time_step']}_lower": list_options}
    else:
        options = [f"{value['level_type']}.json", f"{value['level_type']}.csv"]

    return options

pn.widgets.NestedSelect(
    options=list_options,
    levels=["time_step", "level_type", "file_type"],
)
```

This is useful if you are trying to use options from a hosted source.

Using `pn.cache` here can help improve user experience and reduce the risk of rate limits.

```python
import panel as pn
pn.extension()

@pn.cache()
def list_options(level, value):
    value_path = "/".join(list(value.values()))
    url = f"https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis/{value_path}"

    options = [var.rstrip("/") for var in pd.read_html(url)[0]["Name"].dropna()[1:]]
    if level == "time_step":
        options = {option: list_options for option in options if option[0].isupper()}
    elif level == "level_type":
        options = {option: list_options for option in options if option[0].islower()}
    else:
        options = [option for option in options if option.endswith(".nc")]

    return options

select = pn.widgets.NestedSelect(
    options=list_options,
    levels=["time_step", "level_type", "file"],
)
select
```

`levels` also accepts a list of dicts, where each dict contains the type of widget and its corresponding kwargs.

```python
select = pn.widgets.NestedSelect(
    options={
        "GFS": {
            "0.25 deg": ["00Z", "06Z", "12Z", "18Z"],
            "0.5 deg": ["00Z", "12Z"],
            "1 deg": ["00Z", "12Z"],
        },
        "NAME": {
            "12 km": ["00Z", "12Z"],
            "3 km": ["00Z", "12Z"],
        },
    },
    value={"Model": "NAME", "Resolution": "12 km", "Initialization": "00Z"},
    max_width=500,  # these following kwargs will be inherited by the widgets, unless overridden
    sizing_mode="stretch_width",
    levels=[
        {"name": "Model", "type": pn.widgets.RadioButtonGroup, "color": "primary"},
        {"name": "Resolution", "type": pn.widgets.Select, "max_width": 300},
        {"name": "Initialization", "type": pn.widgets.DiscreteSlider, "width": 100, "sizing_mode": "fixed"},
    ],
)
select
```

---
