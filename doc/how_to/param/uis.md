# Generate Widgets from `Parameters`

This guide addresses how to generate UIs from Parameterized classes without writing any GUI related code.

```{admonition} Prerequisites
1. The [Param User Guide](https://param.holoviz.org/index.html) provides the conceptual foundation for use of `Parameterized` objects.
```

---

Parameters are Python attributes extended using the [Param library](https://param.holoviz.org) to support types, ranges, and documentation, which turns out to be just the information you need to automatically create widgets for each parameter.

## Declaring and displaying parameters

Internally parameters have a mapping that generates widgets appropriate for each type. This means that by declaring a `Parameterized` class we can automatically generate a full UI. Let us declare a `BaseClass`:

```{pyodide}
import param
import panel as pn
import pandas as pd
import datetime as dt

pn.extension()

class BaseClass(param.Parameterized):
    x                       = param.Parameter(default=3.14, doc="X position")
    y                       = param.Parameter(default="Not editable", constant=True)
    string_value            = param.String(default="str", doc="A string")
    num_int                 = param.Integer(default=50000, bounds=(-200, 100000))
    unbounded_int           = param.Integer(default=23)
    float_with_hard_bounds  = param.Number(default=8.2, bounds=(7.5, 10))
    float_with_soft_bounds  = param.Number(default=0.5, bounds=(0, None), softbounds=(0,2))
    unbounded_float         = param.Number(default=30.01, precedence=0)
    hidden_parameter        = param.Number(default=2.718, precedence=-1)
    integer_range           = param.Range(default=(3, 7), bounds=(0, 10))
    float_range             = param.Range(default=(0, 1.57), bounds=(0, 3.145))
    dictionary              = param.Dict(default={"a": 2, "b": 9})
```

and then render the resulting UI using Panel:

```{pyodide}
pn.Param(BaseClass.param)
```

By changing a widget and re-running the following outputs, we can see that changes in the widgets are automatically reflected in Python:

```{pyodide}
BaseClass.unbounded_int
```

```{pyodide}
BaseClass.num_int
```

The reverse is also true; editing a parameter from Python will automatically update any widgets that were generated from the parameter:

```{pyodide}
BaseClass.num_int = 1
pn.Param(BaseClass.param.num_int)
```

Passing the ``.param`` object renders the full set of widgets, while passing a single parameter will display just one widget. In this way we can easily declare exactly which parameters to display:

```{pyodide}
pn.Row(BaseClass.param.float_range, BaseClass.param.num_int)
```

## Advanced parameters

The `BaseClass` primarily declared simple parameters, however there are a wide range of parameter types covering many use cases. Below we define a subclass with some of these additional parameter types.

```{pyodide}
class Example(BaseClass):
    """An example Parameterized class"""

    timestamps = []

    boolean                 = param.Boolean(default=True, doc="A sample Boolean parameter")
    color                   = param.Color(default='#FFFFFF')
    date                    = param.Date(default=dt.datetime(2017, 1, 1),
                                         bounds=(dt.datetime(2017, 1, 1), dt.datetime(2017, 2, 1)))
    dataframe               = param.DataFrame(default=pd.DataFrame({'A': [1, 2, 3]}))
    select_string           = param.Selector(default="yellow", objects=["red", "yellow", "green"])
    select_fn               = param.Selector(default=list,objects=[list, set, dict])
    int_list                = param.ListSelector(default=[3, 5], objects=[1, 3, 5, 7, 9], precedence=0.5)
    single_file             = param.FileSelector(path='../../*/*.py*', precedence=0.5)
    multiple_files          = param.MultiFileSelector(path='../../*/*.py?', precedence=0.5)
    record_timestamp        = param.Action(default=lambda x: x.timestamps.append(dt.datetime.utcnow()),
                                           doc="""Record timestamp.""", precedence=0.7)

example = Example()

pn.Param(example.param)
```

For example, the `Example.timestamps` Parameter records the timestamps from every "record timestamp" button press above. Rerun the code block below after clicking the button in order to see the output in the docs.

```{pyodide}
Example.timestamps
```

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index) for context on this and other Panel APIs
