Comparing Panel and Voila
=========================

Panel and Voila run on very different server architectures. While both run Tornado under the hood, Panel uses Bokeh server while Voila uses the Jupyter Server. These two server architectures differ in the fact that Jupyter will launch a new Python kernel for each user, while the Bokeh server can serve multiple users on the same process. This has two major implications:

1. The per-user overhead for a Bokeh app is much lower. Once the relevant libraries are imported there is only a tiny bit of overhead for creating a new session. The Jupyter server on the other hand launches an entirely new process with all the overhead that entails, e.g. for a session that imports nothing but pandas and matplotlib that is 75 MB of per-user overhead.

2. Since a Bokeh server shares a single process for multiple sessions data or processing can also be shared between the different sessions. This makes it possible to further reduce the memory footprint of a bokeh app.

The other major difference between Panel and Voila is the way it can be used in the notebook. Voila is built mainly around the notebook format. By default all output in the notebook is included in the rendered Voila app, this means existing notebooks can be served as apps but also means that if we want to hide certain outputs a whole custom template is required. Panel takes a different approach in that output needs to be explicitly wrapped in a Panel object and marked as being "servable". 

From a user perspective the last major difference between the Panel and Voila is the types of output that can be included. Voila works with any output that can be rendered inside the Jupyter notebook and is particularly well integrated with ipywidgets based interactive components. Panel currently renders a wide range of objects but does not yet allow rendering ipywidgets based components. This is something we are actively working on, to make it possible to include ipywidgets components in a Panel app and include Panel components in a Voila app.
