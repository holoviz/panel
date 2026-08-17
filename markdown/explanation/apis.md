## APIs

In this section we will discuss the principles and design decisions
behind Panel’s APIs in order to guide you towards the best approach for
structuring your applications. We begin with a set of explanations
behind the use of Param in Panel, how it unlocks reactive approaches to
write applications and contrast function and class based approaches for
writing apps.

Parameters in Panel

Background on the use of Param in Panel.

[Param in Panel](api/param.md)

Reactivity in Panel

A deep dive into the reactive and callback based APIs in Panel.

[Reactivity in Panel](api/reactivity.md)

Functions vs Classes

A discussion that contrasts function and class based APIs in Panel.

[Classes vs functions in Panel: understanding the
tradeoff](api/functions_vs_classes.md)

Next let us contrast the different APIs offered by Panel by applying
them to a particular problem.

 1.
Reactive API

Linking functions or methods to widgets using
`pn.bind` or the equivalent
`pn.depends` decorator.

[Reactive API](api/reactive.md)

 2.
Declarative API

Declare *Parameters* and their ranges in
`Parameterized` classes, then get GUIs (and
value checking!) for free.

[Declarative API](api/parameterized.md)

 3.
Callbacks API

Generate a UI by manually declaring callbacks that update panels or
panes.

[Callbacks](api/callbacks.md)

Finally let’s look at some examples demonstrating how each API can be
applied to build the same app:

Stock Explorer - Callback API

Build a stock explorer app using the
`.param.watch` callback API.

[Stock Explorer - Callback API](api/examples/stocks_callbacks.md)

Stock Explorer - Declarative API

Build a stock explorer app using the Param based declarative API.

[Stock Explorer - Declarative API](api/examples/stocks_declarative.md)

Stock Explorer - Reactive API

Build a stock explorer app using the reactive API.

[Stock Explorer - Reactive API](api/examples/stocks_reactive.md)

Outlier Explorer - Declarative API

Build a simple outlier explorer app using the declarative API.

[Declarative API with Class-Based Approach](api/examples/outliers_declarative.md)
