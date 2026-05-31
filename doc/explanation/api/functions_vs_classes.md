## Classes vs functions in Panel: understanding the tradeoff

In Panel, there are two main ways to structure reactive code: binding functions with `pn.bind` and `pn.rx`(the [reactive API](../../explanation/api/reactive.md)), or building classes that extend `param.Parameterized` or `pn.viewable.Viewer` (the [declarative API](../../explanation/api/parameterized.md)). Both approacheas are valid, and the right choice depends on what you're building.

### Why functions feel natural at first

The reactive/function approach maps onto how most people already think about programming: you write a function that takes inputs and returns an output, then tell Panel which widgets correspond to which arguments. The code stays close to your existing analysis or visualization logic. You don't need to learn class inheritance or `param`'s parameter system. And because `pn.bind` works like `functools.partial`, it's easy to reason about: bind a widget here, get a reactive function there.

This works especially well when you're wrapping code you didn't write, or when you want to keep Panel-specific wiring strictly separate from your domain logic. The binding lives in one place, the computation in another, and neither needs to know about the other.

### Where functions start to struggle: the state problem

The cost becomes visible as soon as your app needs to share state between multiple parts of the UI.

Consider a dashboard that filters a dataset by year range and manufacturer. With `pn.bind`, the widgets are plain Python variables. If a table and a chart both need to reflect the current filter state, you bind both to the same widgets, manageable with two views. But each new view means repeating the same widget references. If the filter logic changes, you update it in every bound function separately. And because the widgets have no single owner, any part of the app that needs to know "what's currently selected?" has to reach into the layout to find out. State is scattered across the codebase rather than living in one place.

### What classes give you: a single source of truth

The class-based approach solves this by declaratively expressing state as parameters, giving state a home. Instead of free-floating widget variables, you create a dedicated object whose job is to hold the current selection as `param.Parameter` attributes. Any part of the app that needs to know what the user has selected asks that object directly.

Other objects can declare, using `@param.depends`, that they should recompute when those parameters change. The logic for what to do when state changes lives in one place, not spread across multiple `pn.bind` calls. Any number of views can all reference the same state-holding object, and when something changes they update automatically — without any view needing to know anything about the widgets that caused the change.

### Separation of concerns

This structure naturally pushes you toward giving each class a single, clear responsibility: one class holds the current user selections, another handles data transformation, another handles presentation. Each piece can be developed and reasoned about independently.

The practical consequence is testability. Because state lives in `param.Parameter` attributes rather than widget values, you can test data transformation logic by constructing an object, setting its parameters directly, and asserting on the output, no widgets, no layout, no browser. You can change how something is displayed without touching any of the underlying computation. With a pure function approach, this separation is much harder to maintain, because the layout code names the widgets and maps them to specific function arguments, so changes to either tend to ripple across both.

### Coupling and portability

There is a genuine tradeoff with `pn.bind`: the GUI code knows about the domain code, but the domain code knows nothing about Panel. Your analysis functions stay portable and testable outside any app context.

The class-based approach is more nuanced. Classes that hold state or handle data transformation can be written as pure `param.Parameterized` subclasses with no Panel dependency whatsoever. They're just Python objects with reactive parameters, and they work fine in a test suite or a script that never imports Panel. The Panel coupling is confined to the presentation layer: classes that extend `pn.viewable.Viewer` and know how to render themselves. This is actually a cleaner separation than it might first appear. You can develop and test all of your state and logic classes in isolation, then write thin Viewer subclasses that know how to display them.

### Imperative code still has a place

Neither approach replaces imperative `.param.watch` or `@depends(..., watch=True)` entirely. Watchers are the right tool for side effects: writing a log entry when something changes, persisting user preferences, triggering a notification, or updating shared state on a class. The key distinction is between *derivations* (outputs that are a pure function of current state) and *effects* (things that happen as a consequence of state changes). Declarative code handles derivations well; imperative code handles effects well. Mixing them, i.e. using watchers to compute derived values, or using `@param.depends` to trigger side effects, leads to code that's hard to follow as the app grows.

### A practical rule of thumb

If you're wrapping an existing function for a notebook or a small exploratory app, `pn.bind` is almost certainly the right choice: minimal, clear, and Panel-agnostic. If you're building something with multiple views sharing a single data source, logic that needs to be tested in isolation, or components that will be reused across layouts, the class-based approach will pay off quickly. The two patterns aren't mutually exclusive either, a class-based app might use `pn.bind` or another reactive construct internally for a simple one-off output, and a function-based app might introduce a class once some piece of state becomes complex enough to deserve a home of its own.
