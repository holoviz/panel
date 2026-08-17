# Create Layouts With ReactiveHTML

In this guide we will show you how to build custom layouts using HTML and `ReactiveHTML`.

## Layout a single parameter

You can layout a single object as follows.

```python
import panel as pn
import param

from panel.custom import Child, ReactiveHTML

pn.extension()

class LayoutSingleObject(ReactiveHTML):

    object = Child(allow_refs=False)

    _template = """
    
      <h1>Temperature</h1>
      <h2>A measurement from the sensor</h2>
      ${object}
    
"""

dial = pn.widgets.Dial(
    label="°C",
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

## Layout multiple parameters

```python
import panel as pn
import param

from panel.custom import Child, ReactiveHTML

pn.extension()

class LayoutMultipleValues(ReactiveHTML):
    object1 = Child()
    object2 = Child()

    _template = """
    
        <h1>Object 1</h1>
        ${object1}
        <h1>Object 2</h1>
        ${object2}
    
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

```python
print(type(layout.object1), type(layout.object2))
```

Lets for fun try another example

```python
LayoutMultipleValues(
    object1="Do you like **beat boxing**?",
    object2="https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    styles={"border": "2px solid lightgray"},
)
```

## Layout as literal `str` values

If you want to show the *literal* `str` value of your parameter instead of the `pn.panel` return value you can configure that via the `_child_config` attribute.

```python
import panel as pn
import param

from panel.custom import ReactiveHTML

pn.extension()

class LayoutLiteralValues(ReactiveHTML):
    object1 = param.String()
    object2 = param.String()

    _child_config = {"object1": "literal", "object2": "literal"}

    _template = """
    
    
      <h1>Object 1</h1>
      ${object1}
      <h1>Object 2</h1>
      ${object2}
    
    """

layout = LayoutLiteralValues(
    object1="This is the **value** of `object1`", object2="This is the **value** of `object2`",
    styles={"border": "2px solid lightgray"},
)
layout.servable()
```

Lets check the types

```python
print(type(layout.object1), type(layout.object2))
```

## Layout a list of objects

If you want to want to layout a dynamic `List` of objects you can use a *for loop*.

```python
import panel as pn
import param

from panel.custom import Children, ReactiveHTML

pn.extension()

class LayoutOfList(ReactiveHTML):

    objects = Children()

    _template = """
    
        {% for object in objects %}
            <h1>Object {{ loop.index0 }}</h1>
            ${object}
            <hr/>
        {% endfor %}
    
"""

LayoutOfList(objects=[
    "I **love** beat boxing",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "Yes I do!"
], styles={"border": "2px solid lightgray"}).servable()
```

The component will trigger a rerendering if you update the `List` value.

## Create a list like layout

If you want to create a *list like* layout similar to `Column` and `Row`, you can combine `ListLike` and `ReactiveHTML`.

```python
import panel as pn
import param

from panel.custom import ReactiveHTML
from panel.layout.base import ListLike

pn.extension()

class ListLikeLayout(ListLike, ReactiveHTML):
    objects = param.List()

    _template = """
    
      {% for object in objects %}
        <h1>Object {{ loop.index0 }}</h1>
        ${object}
        <hr/>
      {% endfor %}
    
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

## Layout a dictionary

If you want to layout a dictionary, you can use a for loop on the `.items()`.

```python
import panel as pn
import param

from panel.custom import ReactiveHTML

pn.extension()

class LayoutOfDict(ReactiveHTML):
    object = param.Dict()

    _template = """
    
    {% for key, value in object.items() %}
      <h1>{{ loop.index0 }}. {{ key }}</h1>
      ${value}
      <hr/>
    {% endfor %}
    
    """

LayoutOfDict(object={
    "Intro":  "I **love** beat boxing",
    "Example": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Beatboxset1_pepouni.ogg",
    "*Outro*": "Yes I do!"
}, styles={"border": "2px solid lightgray"}).servable()
```
