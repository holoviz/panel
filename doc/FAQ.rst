FAQ
===

Here is a list of questions we have either been asked by users or
potential pitfalls we hope to help users avoid:


**Q: What libraries are supported?**

**A:**  We are currently keeping the list at https://github.com/pyviz/panel/issues/2, but hope to move that into the real docs soon.



**Q: Does it matter which plotting library I use with Panel?**

**A:** Some libraries provide deeply interactive objects (e.g. Bokeh and Plotly), and so if you want the user to interact with individual subelements of a plot, you should use one of those libraries. Otherwise, just use any supported library that you prefer!


**Q: How do I add support for a library or datatype not yet supported?**

**A:** It depends. If the object already has one of the usual IPython ``_repr_X_`` rich display methods (where X is png, jpg, or html), then it is very likely to work already. Try it!  If it doesn't have a rich display method, check to see if you can add one as a PR to that project -- they are very useful for many cases other than Panel, too. Otherwise, adding support is quite easy for anything that can somehow return an image or some HTML. If it can return an image in any way, see the ``panel.pane.Matplotlib`` implementation as a starting point; you just need to be able to call some method or function that returns an image, and the rest should be simple.

If you want an even richer JavaScript-based representation, it will be more difficult to add that, but you can see the ``pane.Bokeh`` class and the ``panel.holoviews`` and ``panel.plotly`` modules for examples.


**Q: How does Panel relate to Bokeh?**

**A:** Panel is built on infrastructure provided by Bokeh, specifically Bokeh's  model base classes, layouts, widgets, and server. But Panel does not require using any of Bokeh's plotting support. This way you can make use of a solid, well supported low-level toolkit (Bokeh) to build apps and dashboards for your own plots from any supported library.

Conversely, what Panel adds on top of Bokeh is full bidirectional communication between Python and JavaScript both in a Jupyter session (classic notebook or Jupyter Lab) and in a standalone Bokeh server, making it trivial to move code between Jupyter and server contexts. It then uses this two-way "comms" support to provide reactive widgets, containers, and views that make it simple to put together widget-controlled objects accessible from either Python or JavaScript. Finally, Panel adds a large set of wrappers for common plot and image types so that they can easily be laid out into small apps or full dashboards.


**Q: Why do I get an error "Javascript error adding output! TypeError: Cannot read property 'comm_manager' of undefined"?**

**A:** This error usually means that you forgot to run panel.extension() in a notebook context to set up the code for communicating between JavaScript and Python.  It's easy to get confused and think you don't need that line, because notebooks will often work fine as long as *some* notebook somewhere in your Jupyter session has run the command, but the only reliable way to make the communication channels available is to make sure *every* notebook includes this command.


**Q: Why is the spacing messed up in my panel?**

**A:** Panels are composed of multiple Panes (or other Viewable objects). There are two main ways the spacing between viewable objects can be incorrect: either the object is not reporting its correct size, or the layout engine is not laying things out reasonably. Some pane types are unable to discover the size of what is in them, such as ``pane.HTML``, and for these you will need to provide explicit ``height`` and/or ``width`` settings (as in ``pn.Row(pn.panel(obj, height=300))``. Other spacing problems appear to be caused by issues with the Bokeh layout system, which is currently being improved.  In the meantime you should be able to use ``pn.Spacer(height=..., width=...)`` to adjust spacing manually when needed, with either positive or negative heights or widths.


**Q: Why is my object being shown using the wrong type of pane?**

**A:** A global set of precedence values is used to ensure that the richest representation of a given object is chosen when you pass it to a Row or Column. However, you are also welcome to instantiate a specific Pane type explicitly, as in ``pn.Row(pane.HTML(obj, height=300))``.  If the default Pane type is fine but you still want to be able to pass specific options like width or height in this way, you can use the pn.panel function explicitly, as in  ``pn.Row(pn.panel(obj, height=300))``.


**Q: Why doesn't my Matplotlib plot update in a notebook?**

**A:** Matplotlib pyplot users often use `%matplotlib inline`, which shows plots as a "side effect" in a Jupyter notebook, rather than using the cell's return value like Python literals and other objects do. Panel callbacks like those accepted for `pn.interact()` work on the return value of the callback, which is then provided as the return value of the cell, and thus directly display without any requirements for side effects.  So, if you create a Matplotlib plot that would magically appear via `%matplotlib inline`, for Panel you need to ensure that the callback actually returns a value, rather than counting on this side effect.  Specifically, if you have a callback with some Matplotlib plotting calls, you can add `return plt.gcf()` to your callback to make the current figure be returned, which will ensure that your plot is displayed properly.


**Q: How does Panel relate to other widget/app/dashboard tools?**

**A:** Panel is currently the only Python tool that fully supports writing live widget and app code in Jupyter Notebooks and then deploying it on standalone web servers. Panel is thus unique in supporting the entire life cycle of working with data: from initial exploration, to adding custom interactivity to make one-off analyses easier, to building a complex dashboard from multiple components, to deploying your polished Python-backed dashboard in a public-facing or on-premises private server, and then iterating by bringing those same components back to the notebook for further exploration and improvement. Other tools support *some* of the same capabilities, but by focusing on only one part of this life cycle they require you to start over when you need to use your work in a different way.

For instance, ipywidgets provide many of the same capabilities as Panel, but they are tightly tied to the Jupyter environment, and are not generally able to be used in a secure standalone server. Dash can develop polished dashboards, but it is not designed for supporting initial exploration in a notebook, and is largely focused on Plotly charts rather than the visualization libraries that you are already using. The components of Dash apps or ipywidgets apps are also tightly tied to that particular delivery mechanism, while Panel also supports developing your domain-specific code in a general way independent of notebooks or apps, separating your content from the details of its presentation. Here's a general overview of what each library supports:


+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|                                      | Panel           | ipywidgets           | Bokeh           | Shiny              | Dash (Plotly)          |
+======================================+=================+======================+=================+====================+========================+
|Provides widgets and layouts          | Yes             | Yes                  | Yes             | Yes                | Yes                    |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports interactive plots            | Yes             | Yes                  | Yes             | Yes                | Yes                    |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Reactive updates in Jupyter notebooks | Yes             | Yes                  | Partial (*)     | No                 | No                     |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Deployable in a server                | Yes             | No                   | Yes             | Yes                | Yes                    |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Fully usable in Jupyter               | Yes             | Yes                  | Partial (*)     | No                 | No, only via iframe    |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports Matplotlib plots             | Yes             | Yes                  | No              | No                 | No                     |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports Bokeh plots                  | Yes             | Yes                  | Yes             | No                 | No                     |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports Plotly plots                 | Yes             | Yes                  | No              | No                 | Yes                    |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports R ggplot plots               | Yes             | No                   | No              | Yes                | No                     |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Supports Altair/Vega plots            | Yes             | Yes                  | No              | Yes                | No                     |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Separates content from presentation   | Yes             | Could eventually     | No              | No                 | No                     |
|                                      |                 | using traitlets      |                 |                    |                        |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
|Servable from public site             | Possible        | As live notebooks    | Possible        | Yes, shinyapps.io  | Yes, Plotly Cloud      |
|                                      | with mybinder   | via mybinder         | with mybinder   |                    |                        |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+
+Servable within private enterprise    | Yes, AE5        | Yes, AE5 (with       | Yes, AE5        | Yes, AE5 or Shiny  | Yes, AE5 or Plotly     |
|network                               |                 | readonly code cells) |                 | Server             | Enterprise             |
+--------------------------------------+-----------------+----------------------+-----------------+--------------------+------------------------+

\* - Bokeh can use live reactive widgets in Jupyter notebooks by launching an embedded server process or using ipywidgets/push_notebook

Each of these libraries are free, open-source software packages, but they can be used with the commercial products
`Anaconda Enterprise (AE5) <https://www.anaconda.com/enterprise/>`__,
`Shiny Server <https://www.rstudio.com/products/shiny-server-pro>`__, or
`Plotly Enterprise <https://plot.ly/products/on-premise>`__ to provide on-premises authenticated deployment services within a private network.
