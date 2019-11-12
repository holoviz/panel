Comparing Panel and Voila
=========================

Panel and Voila both offer ways to deploy Python code as a standalone web server, built on very different server architectures (Bokeh Server for Panel, and Jupyter Server for Voila). Both servers are based on Tornado under the hood, but they differ in the fact that Jupyter will launch a new Python kernel for each user, while the Bokeh server can serve multiple users on the same process. This subtle difference has two major implications:

1. The per-user overhead for a Bokeh app is much lower. Once the relevant libraries are imported, there is only a tiny bit of overhead for creating each new session. The Jupyter server, on the other hand, always launches an entirely new process, with all the overhead that entails. For a session that imports nothing but pandas and matplotlib the per-user overhead is 75 MB, which increases for more complex environments.

2. Since a Bokeh server shares a single process for multiple sessions, data or processing can also be shared between the different sessions where appropriate. Such sharing makes it possible to further reduce the memory footprint of a Bokeh-Server app, to make it practical to support larger numbers of users and to provide faster startup or data-access times.

The other major difference between Panel and Voila is the way they can be used in the notebook. Voila is built mainly around the notebook format. By default all output in the notebook is included in the rendered Voila app, which means existing notebooks can be served as apps unchanged, but then requires a complex custom template if you want to show only a subset of the outputs. Panel takes a different approach in that output needs to be explicitly wrapped in a Panel object and marked as being "servable", which makes it practical for the same notebook to serve both an exploratory purpose (in Jupyter) and act as a deployment (of a subset of the functionality). 

From a user perspective the last major difference between the Panel and Voila is the types of output that can be included. Voila works with any output that can be rendered inside the Jupyter notebook, primarily focusing on ipywidgets-based interactive components. Panel currently renders a wide range of objects, but does not yet allow rendering ipywidgets. Upcoming Bokeh releases in 2019 are expected to add support for ipywidgets, so that the server choice can be made to optimize the other considerations above rather than being determined by the supported components.


Comparing Panel and Bokeh
=========================

- Panel is based on Bokeh, but adds full bidirectional communication support for usage in Jupyter, making the same code fully usable in both notebook and server contexts so that it need not be rewritten for different audiences.

- Panel uses the internal layout and server components of Bokeh, but does not depend on any of Bokeh's plotting, and it can be used equally well with plots from a very wide variety of sources. To use such plots with Bokeh directly would require significant custom coding.


Comparing Panel and Dash
=========================

Panel and Dash can both be used to create dashboards in Python, but take very different approaches:

- Panel provides full, seamless support for usage in Jupyter notebooks, making it simple to add controls and layouts wherever they are needed in a workflow, without necessarily building up to any particular shareable app.  Dash is focused almost exclusively on standalone dashboards, though there are some workarounds available for using Dash in notebooks.

- Panel focuses on helping Python users create apps and dashboards using Python, with a concise and expressive Pythonic syntax. Dash reveals more of the underlying HTML and CSS details, which is useful for customization but is distracting and verbose when exploring datasets in Python.

- Panel is plotting library agnostic, fully supporting a wide range of Python libraries out of the box, including Plotly. Dash has full support for Plotly, but other libraries have only limited support, using extension packages.

- Dash dashboards work entirely on the client side (in the browser) once built, which has the advantage of being highly scalable for many simultaneous clients, but the disadvantage of not being able to perform server-side operations in Python like [Datashader](http://datashader.org).


Comparing Panel and ipywidgets
=========================

Both Panel and ipywidgets (aka Jupyter Widgets) allow Python users to use widgets and create apps and dashboards from Python in Jupyter notebooks and in standalone servers (when paired with Voila). They are based on different, independently developed technologies for doing so, with some implications:

- Panel is based on Bokeh widgets, which were developed separately from the Jupyter ecosystem, and designed from the start for standalone deployments.  Jupyter widgets, as the name suggests, were first developed specifically for the notebook environment, and only relatively recently (in 2019) adapted for standalone deployment. ipywidgets are still arguably better integrated into Jupyter, while Bokeh widgets have more solid support for server contexts.

- ipywidgets expose more of the underlying HTML/CSS styling options, allowing them to be customized more heavily than Bokeh widgets currently allow.
