# Communication Channels

Panel lets you write Python code that corresponds to Javascript/HTML objects in a web browser, which requires some means of communication between the two languages. How this communication is achieved depends on the context in which Panel is used, i.e., whether it is being run in a notebook like Classic Jupyter, in JupyterLab, as a standalone web server, etc. Usually it all Just Works™, but in case it doesn't, or if you want to understand the details or limitations of a particular configuration, this page will explain which technologies are used in which contexts to achieve the required channels of communication.

### Types of communication needed:

1. **One-time Python->JS communication**: Writing Python code, emitting HTML/JS code, and running it in a browser. This is the most basic, one-way, one-time functionality involved, and is needed before any further synchronization could occur.
2. **Ongoing Python->JS synchronization**: Ongoing synchronization of Python objects to JS, with Python running throughout the session and sending updates to JS property values when Python attribute values change. Necessary for dynamically updating the web page to reflect Python state.
3. **Ongoing JS->Python synchronization**: Ongoing synchronization of JS objects to an ongoing Python session, with JS sending updates back to Python when the user makes selections or interacts with widgets.

Normally, any implementation with type 3 communication also has Python->JS synchronization, thus providing full **JS<->Python** bidirectional synchronization propagating updates in either direction as needed for full Python-backed web interfaces.

### Contexts of usage:

- **Output to HTML**: Results can be emailed or put on a standard web server as an HTML file, but supports only type 1 one-time Python->JS communication, since there is no Python process running any more.
- **Notebook**: Requires type 1 and 2 communication, with the user working in Python and expecting corresponding updates in JS. Ideally would also include type 3 JS->Python communication to allow capturing user selections and widget values in the browser, but that depends on the technology used.
- **Server**: Typically includes all three types of communication.

### Libraries/modules with support for communication in these contexts

Here we focus on Panel objects, but this chart also applies to pure Bokeh figures and models, which have similar requirements, as well as objects built on Panel (e.g. HoloViews, GeoViews, and hvPlot objects).

|Comm type| Scenario                                                     | Libraries/modules required |
|:-------:|:-------------------------------------------------------------|:----------------|
| 1       | Bokeh output to .html file                                   | [bokeh](https://github.com/bokeh/bokeh) ([bokeh/io/output.py](https://github.com/bokeh/bokeh/blob/main/bokeh/io/output.py)) |
| 1       | Bokeh used without comms support (in dash, streamlit, JupyterLite, etc.) | [bokeh](https://github.com/bokeh/bokeh) ([bokeh/io/output.py](https://github.com/bokeh/bokeh/blob/main/bokeh/io/output.py)) |
| 1,2     | Bokeh displaying in Classic Jupyter w/o Python sync          | [bokeh](https://github.com/bokeh/bokeh) ([bokeh/io/notebook.py](https://github.com/bokeh/bokeh/blob/main/bokeh/io/notebook.py)) |
| 1,2,3   | Bokeh object in a standalone server                          | [bokeh](https://github.com/bokeh/bokeh) server (or `panel serve`) |
| 1,2     | Bokeh displaying in JupyterLab w/o Python sync               | [jupyter_bokeh](https://github.com/bokeh/jupyter_bokeh) |
| 1,2,3   | Bokeh object as an ipywidget                                 | [jupyter_bokeh](https://github.com/bokeh/jupyter_bokeh) |
| 1,2,3   | Bokeh object served in Voila                                 | [jupyter_bokeh](https://github.com/bokeh/jupyter_bokeh) |
| 1,2,3   | Panel object in vscode, nteract, or ipywidgets notebooks     | [jupyter_bokeh](https://github.com/bokeh/jupyter_bokeh) |
| 1,2,3   | ipywidgets in Bokeh-server apps                              | [ipywidgets_bokeh](https://github.com/bokeh/ipywidgets_bokeh) |
| 1,2,3   | ipywidgets in Bokeh layout in Classic Jupyter                | [ipywidgets_bokeh](https://github.com/bokeh/ipywidgets_bokeh) |
| 1,2,3   | bidirectional Bokeh/Python syncing in Classic Jupyter        | [pyviz-comms](https://github.com/holoviz/pyviz_comms) |
| 1,2,3   | bidirectional Bokeh/Python syncing in JupyterLab             | [pyviz-comms](https://github.com/holoviz/pyviz_comms) |
| 1,2,3   | Panel object in Google colaboratory                          | [pyviz-comms](https://github.com/holoviz/pyviz_comms) + [panel](https://github.com/holoviz/panel) ([panel/viewable.py](https://github.com/holoviz/panel/blob/master/panel/viewable.py)) |
| 1,2,3   | ipywidgets in Bokeh layout in JupyterLab                     | [pyviz-comms](https://github.com/holoviz/pyviz_comms) + [panel](https://github.com/holoviz/panel) ([panel/models/ipywidget.py](https://github.com/holoviz/panel/blob/master/panel/models/ipywidget.py)) |
| 1,2,3   | Panel object in Pyodide/PyScript                             | [panel](https://github.com/holoviz/panel) ([panel/io/pyodide.py](https://github.com/holoviz/panel/blob/main/panel/io/pyodide.py)) |
| 1,2,3   | Panel object in Pyodide/PyScript via Sphinx                  | [nbsite.pyodide](https://github.com/pyviz-dev/nbsite/blob/main/nbsite/pyodide/__init__.py) (& [panel/io/mime_render.py](https://github.com/holoviz/panel/blob/main/panel/io/mime_render.py)) |

If you find the scenario of interest to you above, you can see from the right-most column which library (or which Bokeh or Panel module) implements that functionality, and thus e.g. where to open an issue if something is not working.
