Comparing Panel and Bokeh
=========================

- Panel is based on Bokeh, but adds full bidirectional communication support for usage in Jupyter, making the same code fully usable in both notebook and server contexts so that it need not be rewritten for different audiences.

- Panel uses the internal layout and server components of Bokeh, but does not depend on any of Bokeh's plotting, and it can be used equally well with plots from a very wide variety of sources. To use such plots with Bokeh directly would require significant custom coding.


Comparing Panel and Dash
=========================

Panel and Dash can both be used to create dashboards in Python, but take very different approaches:

- Panel provides full, seamless support for usage in Jupyter notebooks, making it simple to add controls and layouts wherever they are needed in a workflow, without necessarily building up to any particular shareable app.  Dash is focused almost exclusively on standalone dashboards, though there are some workarounds available for using Dash in notebooks.

- Panel focuses on helping Python users create apps and dashboards using Python, with a concise and expressive Pythonic syntax. Dash reveals more of the underlying HTML and CSS details, which is useful for customization but can be distracting during the data-exploration phase of a project.

- Panel is plotting library agnostic, fully supporting a wide range of Python libraries out of the box, including Plotly. Dash has full support for Plotly, but other libraries have only limited support, using extension packages.

- Dash dashboards store their per-user session state in the client (the browser), which has the advantage of being highly scalable for many simultaneous client sessions.  This design requires Dash dashboards to be fully reactive, with logic defined by Python callback functions with no side-effects. In contrast, Panel dashboards store the state for all active sessions in both the server and the client, synchronizing between the two. This design allows Panel dashboards to be written in either an imperative or a reactive style, depending on the preferences of the author, but it results in dashboards that consume resources on the server per user and are thus less directly scalable that those produced by Dash.


Comparing Panel and ipywidgets
==============================

Both Panel and ipywidgets (aka Jupyter Widgets) allow Python users to use widgets and create apps and dashboards from Python in Jupyter notebooks and in standalone servers (when paired with Voila). They are based on different, independently developed technologies for doing so, with some implications:

- Panel is based on Bokeh widgets, which were developed separately from the Jupyter ecosystem, and designed from the start for standalone deployments.  Jupyter widgets, as the name suggests, were first developed specifically for the notebook environment, and only relatively recently (in 2019) adapted for standalone deployment. ipywidgets are still arguably better integrated into Jupyter, while Bokeh widgets have more solid support for server contexts.

- ipywidgets expose more of the underlying HTML/CSS styling options, allowing them to be customized more heavily than Bokeh widgets currently allow.


Comparing Panel and Voila
=========================

Voila is a technology for deploying Jupyter notebooks (with or without Panel code) as standalone web pages backed by Python. Voila is thus one way you can deploy your Panel apps, your ipywidgets-based apps, or any other content visible in a Jupyter notebook. Voila is an alternative to the Bokeh Server component that is available through ``panel serve``; Panel works with either one, and you can deploy with *either* Bokeh Server (panel serve) or Voila.  

So, how do you choose between using Voila or Bokeh server?  First, at present (10/2019), Voila is the only way to deploy an app that contains both Bokeh-based components (including Panel objects) and ipywidgets-based components. So, if you want to deploy apps that contain ipyvolume, ipyleaflet, or bqplot components, you'll need Voila for serving, but you can also use any Panel object you wish, as long as you wrap it as an ipywidget using `jupyter_bokeh <https://github.com/bokeh/jupyter_bokeh>`__.  Just do `import jupyter_bokeh as jb ; jb.ipywidget(panel_obj)` and you can then mix Panel objects with ipywidgets in Voila.

If you don't need ipywidgets, you can use either Bokeh Server or Voila for serving Panel objects. Which one should you choose?  Both servers are based on Tornado under the hood, but they differ in the fact that Jupyter will launch a new Python kernel for each user, while the Bokeh server can serve multiple users on the same process. This subtle difference has two major implications:

1. The per-user overhead for a Bokeh app is much lower. Once the relevant libraries are imported, there is only a tiny bit of overhead for creating each new session. The Jupyter server, on the other hand, always launches an entirely new process, with all the overhead that entails. For a session that imports nothing but pandas and matplotlib the per-user overhead is 75 MB, which increases for more complex environments.

2. Since a Bokeh server shares a single process for multiple sessions, data or processing can also be shared between the different sessions where appropriate. Such sharing makes it possible to further reduce the memory footprint of a Bokeh-Server app, to make it practical to support larger numbers of users and to provide faster startup or data-access times.

The other major difference between Bokeh Server and Voila is the way they process notebook files. Voila is built directly on the notebook format. By default all output in the notebook is included in the rendered Voila app, which means existing notebooks can be served as apps _unchanged_. While that can be useful to get a quick set of plots, an existing notebook is unlikely to be organized and formatted in a way that forms a coherent dashboard, so in practice a notebook will need to be rewritten (some outputs suppressed, others rearranged) before it will make a good Voila dashboard, meaning that you end up with two copies of the notebook (one optimized to be a narrative, storytelling notebook with a series of cells, and another organized as a dashboard. Or you can write a template to select only the cells you want in the dashboard and rearrange them, but then you need to maintain both the notebook and the template separately.

Panel takes a different approach in that output from a notebook cell needs to be explicitly wrapped in a Panel object and marked as being "servable"; cell outputs by default are shown only in the notebook, and not with ``panel serve``.  Panel in fact entirely ignores the fact that your notebook is organized into cells; it simply processes all the cells as Python code, and serves all the items that ended up being marked "servable".  Although this approach means editing the original notebook, it makes it practical for the same notebook to serve both an exploratory or storytelling purpose (in Jupyter) and act as a dashboard deployment (of a designated subset of the functionality). 


Comparing Panel and streamlit
=============================

streamlit is an alternative to all of the above packages. Like Jupyter, streamlit provides an interactive, incremental way to build apps.  Unlike Jupyter's web-based notebook cell editor (but as also supported by Dash, Panel, and Bokeh), streamlit reads Python files written a separate editor. Using a Python source file allows users to choose their favorite editor, though using a web-based editor also has the advantage of making it simple to work locally on remote files. The key difference from those other tools is that with streamlit, the entire Python source file is effectively re-run every time a widget changes value, which has the advantage of not allowing confusing out-of-order execution of notebook cells, but it requires all lengthy computations to be made cacheable, which may not be straightforward. 

Panel, in contrast to streamlit, fully supports Jupyter notebooks, for when you wish to preserve a series of text/code/output steps as an exploratory record, to document a workflow for later reproducibility, or to tell a story about data. Thus Panel does not require you to make a switch between "exploring some data" or "developing an app"; it lets you use widgets and layouts whenever they are useful or appropriate, without ever having a cost to switch between such activities. Of course, Panel does not _require_ Jupyter, and in fact can be used just like streamlit, by launching `bokeh serve file.py --dev`, which will watch the Python file for any changes and re-launch the served app each time. That said, just as for streamlit, Bokeh would need caching mechanisms for such an approach to be viable in practice, and such mechanisms have not previously been considered a high priority for the Bokeh development team.

Unlike streamlit, Panel also supports fully reactive applications, where each widget or component of a plot is explicitly and specifically tied to a bit of computation, re-running only the tiniest bit of code that is needed for that particular action. Overall, 
Panel can be used in a much wider range of applications than streamlit, including exploratory data analysis or capturing a reproducible workflow in a Jupyter notebook, developing a simple streamlit-like app, or developing complex, multi-page responsive apps, all without having to switch frameworks or learn a new set of tools. Panel thus supports the entire life cycle of data science, engineering, or scientific artifacts, not just a narrow task of developing a specific type of simple app.
