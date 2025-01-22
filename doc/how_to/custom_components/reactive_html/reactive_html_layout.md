# Create Layouts With ReactiveHTML

In this guide we will show you how to build custom layouts using HTML and `ReactiveHTML`.

## Layout a single parameter

You can layout a single object as follows.

```{pyodide}
import panel as pn
import param

from panel.custom import Child, ReactiveHTML

pn.extension()

class LayoutSingleObject(ReactiveHTML):

    object = Child(allow_refs=False)

    _template = """
    <div>
      <h1>Temperature</h1>
      <h2>A measurement from the sensor</h2>
      <div id="object">${object}</div>
    </div>
"""

dial = pn.widgets.Dial(
    name="°C",
    value=37,
    format="{value}",
    colors=[(0.40, "green"), (1, "red")],
    bounds=(0, 100),
)
LayoutSingleObject(
    object=dial,
    name="Temperature",
    styles={"border": "2px solid lightgray"},
    sizing_mode="stretch_width",
).servable()
```

:::{note}
- We define the HTML layout in the `_template` attribute.
- We can refer to the parameter `object` in the `_template` via the *template parameter* `${object}`.
  - We must give the `div` element holding the `${object}` an `id`. If we do not, then an exception will be raised. The `id` can be any value, for example `id="my-object"`.
- We call our *object* parameter `object` to be consistent with our built in layouts. But the parameter can be called anything. For example `value`, `dial` or `temperature`.
- We add the `border` in the `styles` parameter so that we can better see how the `_template` layes out inside the `ReactiveHTML` component. This can be very useful for development.
:::

## Layout multiple parameters

```{pyodide}
import panel as pn
import param

from panel.custom import Child, ReactiveHTML

pn.extension()

class LayoutMultipleValues(ReactiveHTML):
    object1 = Child()
    object2 = Child()

    _template = """
    <div>
        <h1>Object 1</h1>
        <div id="object1">${object1}</div>
        <h1>Object 2</h1>
        <div id="object2">${object2}</div>
    </div>
"""

layout = LayoutMultipleValues(
    object1="This is the **value** of `object1`", object2="This is the **value** of `object2`",
    styles={"border": "2px solid lightgray"},
)
layout.servable()
```

You might notice that the values of `object1` and `object2` looks like they have been
rendered as markdown! That is correct.

Before inserting the value of a parameter in the `_template`, Panel transforms the value using `pn.panel`. And for a string value `pn.panel` returns a `Markdown` pane.

Let's verify this.

```{pyodide}
print(type(layout.object1), type(layout.object2))
```

Lets for fun try another example

```{pyodide}
LayoutMultipleValues(
    object1="Do you like **beat boxing**?",
    object2="https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    styles={"border": "2px solid lightgray"},
)
```

## Layout as literal `str` values

If you want to show the *literal* `str` value of your parameter instead of the `pn.panel` return value you can configure that via the `_child_config` attribute.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML

pn.extension()

class LayoutLiteralValues(ReactiveHTML):
    object1 = param.String()
    object2 = param.String()

    _child_config = {"object1": "literal", "object2": "literal"}

    _template = """
    <style>
      .pn-container {height: 100%;width: 100%;}
    </style>
    <div class="pn-container">
      <h1>Object 1</h1>
      <div id="object1">${object1}</div>
      <h1>Object 2</h1>
      <div id="object2">${object2}</div>
    </div>
    """

layout = LayoutLiteralValues(
    object1="This is the **value** of `object1`", object2="This is the **value** of `object2`",
    styles={"border": "2px solid lightgray"},
)
layout.servable()
```

Lets check the types

```{pyodide}
print(type(layout.object1), type(layout.object2))
```

## Layout a list of objects

If you want to want to layout a dynamic `List` of objects you can use a *for loop*.

```{pyodide}
import panel as pn
import param

from panel.custom import Children, ReactiveHTML

pn.extension()

class LayoutOfList(ReactiveHTML):

    objects = Children()

    _template = """
    <div id="container" class="pn-container">
        {% for object in objects %}
            <h1>Object {{ loop.index0 }}</h1>
            <div id="object">${object}</div>
            <hr/>
        {% endfor %}
    </div>
"""

LayoutOfList(objects=[
    "I **love** beat boxing",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "Yes I do!"
], styles={"border": "2px solid lightgray"}).servable()
```

The component will trigger a rerendering if you update the `List` value.

:::{note}

You must

- wrap the `{% for object in objects %}` loop in an HTML element with an `id`. Here it is wrapped with `<div id="container">...</div>`.
- close all HTML tags! `<hr>` is valid HTML, but not valid with `ReactiveHTML`. You must close it as `<hr/>`.

You can optionally

- get the index of the `{% for object in objects %}` loop via `{{ loop.index0 }}`.

:::

## Create a list like layout

If you want to create a *list like* layout similar to `Column` and `Row`, you can combine `ListLike` and `ReactiveHTML`.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML
from panel.layout.base import ListLike

pn.extension()

class ListLikeLayout(ListLike, ReactiveHTML):
    objects = param.List()

    _template = """
    <div id="container" class="pn-container">
      {% for object in objects %}
        <h1>Object {{ loop.index0 }}</h1>
        <div id="object">${object}</div>
        <hr/>
      {% endfor %}
    </div>
"""

layout = ListLikeLayout(
    "I love beat boxing",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "Yes I do!",
    styles={"border": "2px solid lightgray"},
)
layout.servable()
```

You can now use `[...]` indexing and the `.append`, `.insert`, `pop`, ... methods that you would
expect.

:::{note}
You must list `ListLike, ReactiveHTML` in exactly that order when you define the class! The other
way around `ReactiveHTML, NamedListLike` will not work.
:::

## Layout a dictionary

If you want to layout a dictionary, you can use a for loop on the `.items()`.

```{pyodide}
import panel as pn
import param

from panel.custom import ReactiveHTML

pn.extension()

class LayoutOfDict(ReactiveHTML):
    object = param.Dict()

    _template = """
    <div id="container" class="pn-container">
    {% for key, value in object.items() %}
      <h1>{{ loop.index0 }}. {{ key }}</h1>
      <div id="value">${value}</div>
      <hr/>
    {% endfor %}
    </div>
    """

LayoutOfDict(object={
    "Intro":  "I **love** beat boxing",
    "Example": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "*Outro*": "Yes I do!"
}, styles={"border": "2px solid lightgray"}).servable()
```

:::{note}
- We can insert the `key` as a literal value only using `{{ key }}`. Inserting it as a template variable `${key}` will not work.
- We must not give the HTML element containing `{{ key }}` an `id`. If we do, an exception will be raised.
:::
