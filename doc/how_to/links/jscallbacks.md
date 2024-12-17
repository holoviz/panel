# Link Many Objects in Javascript

This guide addresses how to write arbitrary JS callbacks linking one or more components.

```{admonition} Prerequisites
1. The [How to > Link Two Objects in Javascript](./links) guide demonstrates how to use the `.jslink` API to link parameters from two objects in Javascript, which is adequate in most cases.
```

---

Sometimes defining a simple link between two objects is not sufficient, e.g. when there are a number of objects involved. In these cases it is helpful to be able to define arbitrary Javascript callbacks. A very simple example is a very basic calculator which allows multiplying or adding two values, in this case we have two widgets to input numbers, a selector to pick the operation, a display for the result and a button.

To implement this we define a `jscallback`, which is triggered when the `Button.clicks` property changes and provide a number of `args` allowing us to access the values of the various widgets:

```{pyodide}
import panel as pn

pn.extension()

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

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
