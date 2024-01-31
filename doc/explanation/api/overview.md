# API Overview

Panel's approach to expressing interactivity and managing state differs from many other frameworks and offers multiple APIs with different affordances. In this overview section we will try to convey the thinking that led to the different APIs in Panel, providing you with context on when to use which and why. In the process we will try to unpack a number of concepts that are central to most UI frameworks and how these concepts translate into Panel's unique approach.

:::{note}
Panel has gone through a significant evolution over time and many of the concepts discussed here really only fully crystallized when Param 2.0 was released.
:::

## Concepts

The core concept a large part of the discussion will focus on is the difference between reactive and event driven approaches for writing UIs. Panel has placed strong emphasis on innovating to provide novel **reactive** approaches to writing applications. Popular reactive frameworks include spreadsheets like Excel and frontend UI frameworks like React, each of which has a different approach to reactivity, but two core principles are conserved:

1. They are **data-driven**, i.e. the UI updates automatically in response to changes in the data model. In Excel the data model is represented by value of a cell, while React has use state hooks. In Panel the data model is defined by Parameters, i.e. components and user classes define some parameters which drive changes in the UI. In all these frameworks this is achieved by what we will call **data binding**, how precisely this works will be the primary focus of this section.

2. They are **declarative**, i.e. the user, defines what should be rendered and the reactive framework figures out how to efficiently make the required updates. In Excel this is simple, it simply has to re-evaluate any formulas that depend on the changed inputs and then update the cell's output. In React this can be significantly more involved, requiring diffing of the document model and then figuring out the most efficient updates to reflect the latest changes. In Panel this works either by defining a function who's output is diffed or by binding references to a declarative component (if you don't know what that means yet, don't worry, that's what this guide is for).

The alternative to the reactive approach is an event-driven approach, involving callbacks that are triggered by user interactions or other events. This approach usually relies on **imperative** rather than **declarative** programming, i.e. you define step-by-step what should happen when a particular action is triggered. This is usually significantly more cumbersome, especially as an application grows in size and complexity. Even in a relatively simple application where we gather user inputs from multiple widgets and then perform some update we quickly run into problems. Let us take a simple example of an application that has three widgets that gather user input. In a callback based approach we have to register a callback with each of the three widgets and then perform some action as a result:

![Diagram of callback based UI code](../../_static/images/callback_diagram.svg)

The problem we immediately run into if some action we want to take requires more than one of the inputs is how we coordinate these changes. This is why many older callback based frameworks rely on what is called the Model-View-Controller (MVC) pattern, where the **view** that the user interacts with, gathers the inputs, which are fed to a **controller** that is able to coordinate the various events and manipulate the underlying model. This requires significant state handling, which in practice is only really feasible by implement a class based controller.

In the reactive approach things are much simpler, the inputs are bound to a declarative function or component that immediately reflects the required changes in the rendered view:

![Diagram of reactive UI code](../../_static/images/reactive_diagram.svg)

## Reactivity in Panel

Now that we have introduced some of the concepts behind the reactive approaches let's dive into the nitty gritty and try to understand how Panel actually implements the abstract concepts of reactivity in practice. As we discussed previously, reactive approaches rely on **data binding** and we also mentioned that Parameters are the native way for Panel to express the data model. At the implementation level data binding therefore happens by binding parameter state to some component or function. The important thing to understand is that for binding to be expressed in code we have to make a distinction between the parameter **value** and the abstract parameter **reference**. To make this concrete, to perform binding we have to use the parameter **object**, which acts as a proxy or reference for its value. Let's say we have a `TextInput` widget:

```python
text = pn.widgets.TextInput(value='Hello world!')
```

The widget's value parameter value can be accessed with `text.value`, but this represents the value at that point in time. To perform binding we have to access the parameter object with `text.param.value`, this acts as a reference or proxy that can be bound. In Panel there are two main ways of performing data binding, either we can directly bind a reference to a parameter, e.g. we can do:

```python
pn.pane.Markdown(object=text.param.value)
```

This performs data binding between the `value` parameter of the widget and the `object` parameter of the `Markdown` pane and provides a declarative specification of this reactive component. We will refer to this as **component level binding**. This is the simplest and most explicit form of data binding in Panel and has to be distinguished from **function level binding** where we use `pn.bind` to bind a parameter reference to a function:

```python
slider1 = pn.widgets.FloatSlider(start=0, end=10)
slider2 = pn.widgets.FloatSlider(start=0, end=10)

def add(a, b):
    return pn.pane.Str(f'{a=} + {b=} = {a+b}')

pn.Column(slider1, slider2, pn.bind(add, slider1.param.value, slider2.param.value))
```

In this example, we have bound two inputs to the function and return an output, the `Str` pane. Internally a few things will happen to make this work:

1. Panel wraps the bound function in a so called `ParamFunction` pane.
2. The `ParamFunction` pane watches the inputs to the bound function for changes.
3. When a slider is dragged and the input changes the `ParamFunction` will re-evaluate the function with the new inputs and then figure out the appropriate update.

:::{important}
Since Panel cannot know if you have a handle on the `Str` pane that is being returned, it cannot safely update the `Str` pane inplace. Therefore it re-renders the corresponding model every time the inputs change. For complex panes and output this can lead to undesirable flicker. To avoid this you have to tell Panel that the output can be safely updated `inplace`:

```python
pn.param.ParamFunction(pn.bind(add, slider1.param.value, slider2.param.value), inplace=True)
```
:::

Function level binding provides significantly flexibility, e.g. we can write reactive components that change type depending on the input. We could return a different component depending on the value of some widgets and Panel would re-render the output appropriately. However this also means that compared to component level binding, function level binding is significantly less efficient and where possible component level binding should be preferred.

However, if we think back to the diagram above, we can hopefully immediately see the benefit of this reactive approach, whether component or function. In a callback based approach it is immediately unclear how we would combine the state of `slider1` and `slider2` into a single update. Either we have to resort to accessing values directly introducing unseen entanglement of our UI code and logic, quickly resulting in spaghetti code or we have introduce a class that acts as a controller to track the updates and hold the state.

## Reactive References

So far we have explored the difference between reactive and callback based code and gone over component-level and function-level binding to achieve reactivity in Panel. To really understand the power of binding we have to dive a little deeper into what it references are and how they can be bound. In particular we have, so far, focused primarily on Parameters as references. This makes sense since pretty much all reactivity in Panel is ultimately driven by a parameter. However binding parameters on their own is usually not that useful. Thinking back to our simple component-level binding example:

```python
text = pn.widgets.TextInput(value='Hello world!')

pn.pane.Markdown(object=text.param.value)
```

You might have wondered: "why is this useful?". You rarely want to bind the output of a widget directly to some other output or parameter. In practice an output or parameter value will usually be the result of transforming one or more inputs. For this reason Panel (and Param, which it builds on) allows a number of different types to be used as a reference:

1. Parameters: A `Parameter` object is the simplest reference.
2. Widgets: A Panel `Widget` acts as a proxy for its `value` parameter, i.e. passing `text` and `text.param.value` are equivalent in the last example.
3. Bound functions: A function which has other references bound to it using the `pn.bind` helper may also be used as a reference.
4. Reactive Expressions: Param offers so called reactive expressions which act as proxies for their underlying objects and can be chained into arbitrary expressions.
5. Async Generators: Asynchronous generators functions can be used as a reference to drive streaming outputs.

To unpack this a little bit let's go back to our earlier example, which used function level binding to add two values and render the output using a `Str` pane:

```python
slider1 = pn.widgets.FloatSlider(start=0, end=10)
slider2 = pn.widgets.FloatSlider(start=0, end=10)

def add(a, b):
    return pn.pane.Str(f'{a=} + {b=} = {a+b}')

pn.Column(slider1, slider2, pn.bind(add, slider1.param.value, slider2.param.value))
```

As we emphasized earlier, function level binding is actually kind of inefficient, so using a bound function as a reference we can rewrite this to use component level binding instead:

```python
slider1 = pn.widgets.FloatSlider(start=0, end=10)
slider2 = pn.widgets.FloatSlider(start=0, end=10)

def add(a, b):
    return f'{a=} + {b=} = {a+b}'

pn.Column(slider1, slider2, pn.pane.Str(object=pn.bind(add, slider1, slider2))
```
