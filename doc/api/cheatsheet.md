# Cheat Sheet

In order to get the best use out of the Panel user guide, it is important to have a grasp of some core concepts, ideas, and terminology.

## Components

Panel provides three main types of component: ``Pane``, ``Widget``, and ``Panel``. These components are introduced and explained in the [Components](../explanation/components/components_overview.md) guide, but briefly:

* **``Pane``**: A ``Pane`` wraps a user supplied object of almost any type and turns it into a renderable view. When the wrapped ``object`` or any parameter changes, a pane will update the view accordingly.

* **``Widget``**: A ``Widget`` is a control component that allows users to provide input to your app or dashboard, typically by clicking or editing objects in a browser, but also controllable from within Python.

* **``Panel``**: A ``Panel`` is a hierarchical container to lay out multiple components (panes, widgets, or other ``Panel``s) into an arrangement that forms an app or dashboard.

---

## APIs

Panel is a very flexible system that supports many different usage patterns, via multiple application programming interfaces (APIs).  Each API has its own advantages and disadvantages, and is suitable for different tasks and ways of working. The [API guide](../explanation/api/index.md) goes through each of the APIs in detail, comparing their pros and cons and providing recommendations on when to use each.

### [Reactive functions](../how_to/interactivity/index.md)

Defining a reactive function using the ``pn.bind`` function or ``pn.depends`` decorator provides an explicit way to link specific inputs (such as the value of a widget) to some computation in a function, reactively updating the output of the function whenever the parameter changes. This approach is a highly convenient, intuitive, and flexible way of building interactive UIs.

### [``Param``](../how_to/param/index.md)

``Panel`` itself is built on the [param](https://param.pyviz.org) library, which allows capturing parameters and their allowable values entirely independently of any GUI code. By using Param to declare the parameters along with methods that depend on those parameters, even very complex GUIs can be encapsulated in a tidy, well-organized, maintainable, and declarative way. Panel will automatically convert parameter definition to corresponding widgets, allowing the same codebase to support command-line, batch, server, and GUI usage. This API requires the use of the param library to express the inputs and encapsulate the computations to be performed, but once implemented this approach leads to flexible, robust, and well encapsulated code. See the Panel [Param how-to guides](../how_to/param/index.md) for more detail.

### [Callback API](../how_to/links/index.md)

At the lowest level, you can build interactive applications using ``Pane``, ``Widget``, and ``Panel`` components and connect them using explicit callbacks. Registering callbacks on components to modify other components provides full flexibility in building interactive features, but once you have defined numerous callbacks it can be very difficult to track how they all interact. This approach affords the most amount of flexibility but can easily grow in complexity, and is not recommended as a starting point for most users. That said, it is the interface that all the other APIs are built on, so it is powerful and is a good approach for building entirely new ways of working with Panel, or when you need some specific behavior not covered by the other APIs. See the [callback and linking how-to guide](../how_to/links/index.md) for more detail.

---

## Display and rendering

Throughout this user guide we will cover a number of ways to display Panel objects, including [display in a Jupyter notebook](../how_to/notebook/index.md), in a standalone server, by saving and embedding, and more.

### Notebook

All of Panel's documentation is built from Jupyter notebooks that you can explore at your own pace. Panel does not require Jupyter in any way, but it has extensive Jupyter support:

#### ``pn.extension()``

> The Panel extension loads BokehJS, any custom models required, and optionally additional custom JS and CSS in Jupyter notebook environments. It also allows passing any [`pn.config`](../api/config.md) variables.

#### ``pn.ipywidget()``

> Given a Panel model `pn.ipywidget` will return an ipywidget model that renders the object in the notebook. This can be useful for including an panel widget in an ipywidget layout and deploying Panel objects using [Voilà](https://github.com/voila-dashboards/voila/).

#### ``pn.io.push_notebook``

> When working with Bokeh models directly in a Jupyter Notebook any changes to the model are not automatically sent to the frontend. Instead we have to explicitly call `pn.io.push_notebook` on the Panel component(s) wrapping the Bokeh component being updated.

#### Rich display

Jupyter notebooks allow the final value of a notebook cell to display itself, using a mechanism called [rich display](https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display). As long as `pn.extension()` has been called in a notebook, all Panel components (widgets, panes, and panels) will display themselves when placed on the last line of a notebook cell.

### Python REPL and embedding a server

When working in a Python REPL that does not support rich-media output (e.g. in a text-based terminal) or when embedding a Panel application in another tool, a panel can be launched in a browser tab using:

#### ``.show()``

> The ``.show()`` method is present on all viewable Panel objects and starts a server instance then opens a browser tab to point to it. To support working remotely, a specific port on which to launch the app can be supplied.

#### ``pn.serve()``

>Similar to .show() on a Panel object but allows serving one or more Panel apps on a single server. Supplying a dictionary mapping from the URL slugs to the individual Panel objects being served allows launching multiple apps at once. Note that to ensure that each user gets separate session state you should wrap your app in a function which returns the Panel component to render. This ensures that whenever a new user visits the application a new instance of the application can be created.

### Command line

Panel mirrors Bokeh's command-line interface for launching and exporting apps and dashboards:

#### ``panel serve app.py``

> The ``panel serve`` command allows allows interactively displaying and deploying Panel web-server apps from the commandline.

#### ``panel serve app.ipynb``

> ``panel serve`` also supports using Jupyter notebook files, where it will serve any Panel objects that were marked `.servable()` in a notebook cell. This feature allows you to maintain a notebook for exploring and analysis that provides certain elements meant for broader consumption as a standalone app.

### Export

When not working interactively, a Panel object can be [exported to a static file](../how_to/export/index.md).

#### ``.save()`` to PNG

> The ``.save`` method present on all viewable Panel objects allows saving the visual representation of a Panel object to a PNG file.

#### ``.save()`` to HTML

> ``.save`` to HTML allows sharing the full Panel object, including any static links ("jslink"s) between widgets and other components, but other features that depend on having a live running Python process will not work (as for many of the Panel webpages).

### Embedding

Panel objects can be serialized into a static JSON format that captures the widget state space and the corresponding plots or other viewable items for each combination of widget values, allowing fully usable Panel objects to be embedded into external HTML files or emails.  For simple cases, this approach allows distributing or publishing Panel apps that no longer require a Python server in any way. Embedding can be enabled when using ``.save()``, using the ``.embed()`` method or globally using [Python and Environment variables](#Python and Environment variables) on ``pn.config``.

#### ``.embed()``

> The ``.embed()`` method embeds the contents of the object it is being called on in the notebook.

___

## Linking and callbacks

One of the most important aspects of a general app and dashboarding framework is the ability to link different components in flexible ways, scheduling callbacks in response to internal and external events. Panel provides convenient lower and higher-level APIs to achieve both.  For more details, see the [callback and linking how-tos](../how_to/links/index.md) .

### Methods

#### ``.param.watch``

> The ``.param.watch`` method allows listening to parameter changes on an object using Python callbacks. It is the lowest level API and provides the most amount of control, but higher-level APIs are more appropriate for most users and most use cases.

#### ``.link()``

> The Python-based ``.link()`` method present on all viewable Panel objects is a convenient API to link the parameters of two objects together, uni- or bi-directionally.

#### ``.jscallback``

> The Javascript-based ``.jscallback()`` method allows defining arbitrary Javascript code to be executed when some property changes or event is triggered.

#### ``.jslink()``

> The JavaScript-based ``.jslink()`` method directly links properties of the underlying Bokeh models, making it possible to define interactivity that works even without a running Python server.
