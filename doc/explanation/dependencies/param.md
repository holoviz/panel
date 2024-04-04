# Panel and Param

```{pyodide}
import param
import panel as pn

pn.extension()
```

[Param](https://param.holoviz.org/) is a Python package that is foundational in the implementation and usage of Panel, and more generally of the [HoloViz](https://holoviz.org/) tools. Param provides super-charged object attributes, called **Parameters**, that behave like normal Python object attributes but benefit from two major features that are both heavily used in Panel:

- *Parameter* attribute values are runtime validated.
- *Parameters* are objects that can be watched, i.e. you can register callbacks (Python functions or methods) that will be executed when the parameter value changes.

## *Parameterized* and *Parameter* intro

A *Parameterized* class, i.e. a class on which *Parameters* can be set, is created by inheriting from `param.Parameterized`. Most Panel objects (widgets, panels, layouts, templates, etc.) actually inherit from `param.Parameterized`!

```{pyodide}
print(
    issubclass(pn.widgets.FloatSlider, param.Parameterized),
    issubclass(pn.pane.Matplotlib, param.Parameterized),
    issubclass(pn.Column, param.Parameterized),
    issubclass(pn.template.BootstrapTemplate, param.Parameterized)
)
```

Let's create a *Parameterized* class with a single *Parameter*.

```{pyodide}
class A(param.Parameterized):
    x = param.Number()
```

`A` has now an attribute `x` that can be accessed and set as you would normally do with a plain Python class.

```{pyodide}
A.x
```

As each *Parameter* type has a default value, we can instantiate `A` as is.

```{pyodide}
a = A()
a.x
```

Obviously, we can set a new value for `x` on `a`.

```{pyodide}
a.x = 2
a.x
```

In Panel documentation we often refer to the *Parameter **value*** to describe the attribute value.
The *Parameter **object***, i.e. the object declared in the class body and of type `param.Parameter`, can be accessed via the `.param` namespace, both at the class and instance level.

```{pyodide}
A.param.x  # equivalent to A.param['x']
```

```{pyodide}
a.param.x  # # equivalent to a.param['x']
```

The *Parameter* object has methods and attributes that can be useful to interact with. We can for instance access the `default` value of the `x` Parameter.


```{pyodide}
a.param.x.default
```

*Parameterized* classes often don't need a constructor, because the default constructor already allows them to be configured using *Parameters* as constructor arguments. Still, sometimes you do need to customize the constructor of a *Parameterized* class. This happens regularly enough that Param's users have come up with the following convention that you are likely to encounter.

```{pyodide}
class A(param.Parameterized):
    x = param.Number()

    # Naming the keyword arguments `**params` is purely a convention.
    def __init__(self, **params):
        super().__init__(**params)
        self._y = self.x * 2
```

:::{attention}
For an object attribute to be powered by Param you must declare it as a *Parameter*! Otherwise, that attribute will become a regular **class variable**, and as such will be shared across all the instances of that class.

```python
class P(param.Parameterized):
    x = param.Number()  # Good
    w1 = pn.widgets.FloatSlider()  # Very likely you DO NOT want this
    w2 = param.ClassSelector(class_=pn.widgets.FloatSlider)  # Much better!

```
:::

## Runtime type-checking

The class `B` below is created with 4 *Parameters*:

- `t` is a `Number` *Parameter* that only accepts Python `int` and `float` values.
- `i` is an `Integer` *Parameter* that only accepts Python `int` values and that must be within the interval `[5, 15]`
- `s` is a `String` *Parameter* that only accepts Python `str` values and is documented with `doc`.
- `option` is a `Selector` *Parameter* that only accepts one of the values listed in `objects`.


:::{note}
Param offers [many *Parameter* types](https://param.holoviz.org/user_guide/Parameter_Types.html). All of them share a common set of arguments like `default` or `doc`, and some add other arguments such as `bounds` for the numerical *Parameters*.
:::

```{pyodide}
class B(param.Parameterized):
    t = param.Number()
    i = param.Integer(default=10, bounds=(5, 15))
    s = param.String(default='a string', doc='The simulation name')
    option = param.Selector(objects=['a', 'b', 'c'])
```

Once the class is created, the *Parameters* are already active and can be updated, but only if they're valid!

```{pyodide}
# Updating `t` to 2 is valid
B.t = 2

# However updating `i` with a string isn't and raises an error
try:
    B.i = 'bad data'
except Exception as e:
    print(e)
```

The same principle applies at the instance level, both when creating the instance and when updating it later on.

```{pyodide}
# Setting `t` to 3 is valid
b = B(t=3)

# However setting `i` to a string isn't and raises an error
try:
    B(i='bad data')
except Exception as e:
    print(e)
```

```{pyodide}
# Setting `s` to a string is valid
b.s = 'foo'

# However setting `option` to a value not found in `objects` isn't
try:
    b.option = 'bad data'
except Exception as e:
    print(e)
```

As you can see, code inside of *Parameterized* objects and code that uses *Parameterized* objects can often be written without any special error checking, since it knows that only allowed values will ever be present.


## Dependencies and watchers

*Parameters* are objects that can be watched, i.e., you can register callbacks that will be triggered when their value changes.

The class `C` has 3 *Parameters*. Using the `param.depends` decorator, we can declare the callbacks of these classes, i.e. its methods, and the *Parameters* that they depend on:

- `updating_on_t` depends on both `t1` and `t2`.
- `updating_on_s` deponds on `s` only.

By setting `watch=True` (default: `False`), we let Param know that we want it to trigger the callback automatically whenever the *Parameters* it depends on are updated. Without setting `watch`, we're only _declaring_ the dependency between a callback and its *Parameters*, which is information that is stored by Param but not used by it otherwise. Libraries like Panel that read this information can then use the declarations to determine their own flow of program execution, as we will see later.

```{pyodide}
class C(param.Parameterized):
    t1 = param.Number(default=2)
    t2 = param.Number(default=3)
    s = param.String(default='a string')

    @param.depends('t1', 't2', watch=True)
    def updating_on_t(self):
        print(f'New value of t1 and t2: {self.t1}, {self.t2}')

    @param.depends('s')
    def updating_on_s(self):
        print(f'New value of s: {self.s}')

c = C()
```

Let's confirm this behavior by setting new values to these *Parameters*.

```{pyodide}
c.t1 = 0
```

```{pyodide}
c.t2 = 1
```

```{pyodide}
c.s = 'another string'
```

Param offers a more low-level API to set up watchers, with the `watch` function available on the `.param` namespace. `watch` accepts a callback and a list of *Parameter* names, and a few other arguments. The callback will receive an `Event` object, and the new *Parameter* value can be found on its `new` attribute.

```{pyodide}
def callback(event):
    print(event)
    print()
    print(f'Old value of s: {event.old}')
    print(f'New value of s: {event.new}')

# Setting up a watcher that will trigger the callback when `s` changes.
c.param.watch(callback, ['s'])
```

```{pyodide}
c.s = 'new string'
```

## Panel and Param

Panel knows how to map *Parameters* to widgets, and so it can easily generate a set of widgets from *Parameterized* class that control its *Parameters* and trigger any dependent callbacks:

```{pyodide}
class D(param.Parameterized):
    t = param.Number()
    i = param.Integer(default=10, bounds=(5, 15))
    s = param.String(default='a string', doc='The simulation name')
    option = param.Selector(objects=['a', 'b', 'c'])

    @param.depends('t', 'i')
    def compute(self):
        return self.t * self.i

d = D()

pn.panel(d.param)
```

Panel, when given a method decorated with `@param.depends`, will re-run the method and render its new output every time one of the *Parameters* it depends on change:

```{pyodide}
pn.Row(d.param.t, d.param.i, d.compute)
```

Because the displayable objects provided by Panel are all *Parameterized* objects with their own set of *Parameters*, they can all be watched. We can for instance hide a widget (setting `widget.visible` to `False`) by watching the value of another widget:

```{pyodide}
checkbox = pn.widgets.Checkbox(value=True)
slider = pn.widgets.FloatSlider()

def hide(event):
    slider.visible = event.new

checkbox.param.watch(hide, 'value')

pn.Row(checkbox, slider)
```

Using `.param.watch` as done just above is a valid (albeit pretty verbose!) way to set up some interactivity between Panel components. Panel also provides a much more natural "reactive" API, allowing you to bind the value of two *Parameters* together, or to bind the value of a *Parameter* to a callback that depends on some additional *Parameters*. In the example below, `tinput.visible` and `output.visible` will be updated whenever `checkbox.value` changes (clicking on the checkbox), and the value of `output.object` will be updated whenever `tinput.value` changes, that value being transformed by the `boldit` callback.

```{pyodide}
checkbox = pn.widgets.Checkbox(value=True)
tinput = pn.widgets.TextInput(value='some text always bold', visible=checkbox.param.value)

def boldit(value):
    return f'**{value}**'

output = pn.pane.Markdown(object=pn.bind(boldit, tinput.param.value), visible=checkbox.param.value)
```

```{pyodide}
pn.Row(checkbox, tinput, output)
```

As you can see, *Parameters* offer a very generic mechanism for your Python code to declare options that control it, and Panel's Param support allows you to work naturally with any combination of objects and their *Parameters*.

## Related Resources

- See [Param's documentation](https://param.holoviz.org/)
- See [How-to > Declare UIs with Declarative API](../../how_to/param/index.md).
