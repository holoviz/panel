# Param in Panel

Panel and other projects in the HoloViz ecosystem all build on Param. Param provides a framework to add validation, documentation and interactivity to a project. It is similar to more modern projects such as Pydantic but focuses primarily on providing APIs that make it easy to express complex dependencies, reactivity and UI interactions.

To get a better understanding of Param itself check out the [user guide in the Param documentation](https://param.holoviz.org/user_guide/index.html) but here we will focus on the use of Param in Panel and how it powers all reactive and callback based APIs.

## What is a Parameter?

Parameters are objects that express the semantics of a value of an attribute on an object, e.g. the `value` of `Widget`, i.e. whether it is a number or a string. Generally Parameters are broader than Python types because they deal with semantics not the specific representation of a value. A `Parameter` object also acts as a reference to the underlying value, which is incredibly useful when trying to add interactivity to a UI and forms the basis of most of the reactive APIs in Panel.

To make this more concrete let's look at a parameter definition, in this case for the Panel `TextInput` widget `value` parameter:

```python
class TextInput(Widget):

    ...

    value = param.String(default='', allow_None=True, doc="""
        Initial or entered text value updated when <enter> key is pressed.""")
```

A `Parameter` must be defined inside a class and that class must be a subclass of `Parameterized`. We can also see that it is of type `param.String`, defines a default of `''` and allows `None` value. It also has a docstring which gives us some information about it. All Panel components are configurable via parameters.

:::{attention}
The difference between a parameter value and the parameter itself is a central concept to really understand how Panel works, so make sure you pay attention to the next part.
:::

Let's start by working with a `TextInput` widget:

```{pyodide}
import panel as pn

text_input = pn.widgets.TextInput(value='A string!')

text_input
```

We can access the current value of the widget:

```{pyodide}
text_input.value
```

But we can also access the `Parameter` instance for value:

```{pyodide}
text_input.param.value
```

Not only does the parameter hold the various metadata and validation options for the parameter but in many scenarios it can be used as a stand-in, proxy or reference for the actual value which can then be resolved interactively whenever the value changes.

## References

The concept of a reference is crucial to using Panel effectively, as much of the [reactivity](reactivity.md) in Panel is built on top of the idea of reference binding. The other piece (i.e. the binding) is that parameters can be given a reference, which they will internally resolve and update whenever the reference updates. In param itself this has to be declared by declaring `allow_ref=True` on the parameter, in Panel effectively all parameters automatically enable this functionality and also allow support for `nested_refs=True` where possible.

Let us explore this with a simple example:

```{pyodide}
import param

class TextFormatter(param.Parameterized):

    text = param.String(allow_refs=True)

	def __str__(self):
	    return f'**{self.text}**'

text_input = pn.widgets.TextInput(value='A string!')

TextFormatter(text=text_input.param.value)
```
