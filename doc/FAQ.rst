FAQ
===

Here is a list of questions we have either been asked by users or
potential pitfalls we hope to help users avoid:


**Q: What libraries are supported?**

**A:**  We are currently keeping the list at https://github.com/pyviz/panel/issues/2, but hope to move that into the real docs soon.



**Q: Does it matter which plotting library I use with Panel?**

**A:** Some libraries provide deeply interactive objects (e.g. Bokeh and Plotly), and so if you want the user to interact with individual subelements of a plot, you should use one of those libraries.  Otherwise, just use any supported library that you prefer!


**Q: How do I add support for a library or datatype not yet supported?**

**A:** It depends.  If the object already has one of the usual IPython `_repr_X_` rich display methods (where X is png, jpg, or html), then it is very likely to work already.  Try it!  If it doesn't have a rich display method, check to see if you can add one as a PR to that project -- they are very useful for many cases other than Panel, too.  Otherwise, adding support is quite easy for anything that can somehow return an image or some HTML.  If it can return an image in any way, see the `panel.pane.Matplotlib` implementation as a starting point; you just need to be able to call some method or function that returns an image, and the rest should be simple.

If you want an even richer JavaScript-based representation, it will be more difficult to add that, but you can see the `pane.Bokeh` and `pane.HoloViews` classes and the `panel.plotly` module for examples.


**Q: How does Panel relate to Bokeh?**

**A:** Panel is built on infrastructure provided by Bokeh, specifically Bokeh's  model base classes, layouts, widgets, and server.  But Panel does not require using any of Bokeh's plotting support.  This way you can make use of a solid, well supported low-level toolkit (Bokeh) to build apps and dashboards for your own plots from any supported library.

Conversely, what Panel adds on top of Bokeh is full bidirectional communication between Python and JavaScript both in a Jupyter session (classic notebook or Jupyter Lab) and in a standalone Bokeh server, making it trivial to move code between Jupyter and server contexts.  It then uses this two-way "comms" support to provide reactive widgets, containers, and views that make it simple to put together widget-controlled objects accessible from either Python or JavaScript.  Finally, Panel adds a large set of wrappers for common plot and image types so that they can easily be laid out into small apps or full dashboards.


**Q: Why do I get an error "Javascript error adding output! TypeError: Cannot read property 'comm_manager' of undefined"?**

**A:** This error usually means that you forgot to run panel.extension() in a notebook context to set up the code for communicating between JavaScript and Python.


**Q: Why is the spacing messed up in my panel?**

**A:** Panels are composed of multiple Panes (or other Viewable objects).  There are two main ways the spacing between viewable objects can be incorrect: either the object is not reporting its correct size, or the layout engine is not laying things out reasonably.  Some pane types are unable to discover the size of what is in them, such as `pane.HTML`, and for these you will need to provide explicit `height` and `width` settings (as in `pp.ROW(pane.HTML(obj, height=300))`.  Other spacing problems appear to be caused by issues with the Bokeh layout system, which is currently being improved.


**Q: Why is my object being shown using the wrong type of pane?

**A:** A global set of precedence values is used to ensure that the richest representation of a given object is chosen when you pass it to a Row or Column.  However, you may need to select a specific Pane type explicitly, e.g. if you want to see widgets for the parameters of a type that also has a `_repr_png_`, or if you need a place to supply width, height.  In this case, you can pick a specific Pane type yourself and instantiate it with any parameters you prefer, as in 
`pp.ROW(pane.HTML(obj, height=300))`.


**Q: How does Panel relate to other app/dashboard tools?

**A:** Panel is currently the only tool with full support for showing the same objects in a Jupyter notebook and in a standalone deployable server:


+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|                                     | Panel           | ipywidgets          | Bokeh           | Shiny              | Dash (Plotly)          |
+=====================================+=================+=====================+=================+====================+========================+
|Provides widgets                     | Yes             | Yes                 | Yes             | Yes                | Yes                    |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Provides layout                      | Yes             | Yes                 | Yes             | Yes                | Yes                    |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Supports interactive plots           | Yes             | Yes                 | Yes             | Yes                | Yes                    |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Reactive updates in Jupyter notebooks| Yes             | Yes                 | No              | No                 | No                     |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Deployable in a server               | Yes             | No                  | Yes             | Yes                | Yes                    |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Fully usable in Jupyter              | Yes             | Yes                 | Only as         | No                 | No, only via           |
|                                     |                 |                     | embedded server |                    | iframe                 |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Supports Matplotlib plots            | Yes             | Yes                 | No              | No                 | No                     |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Supports Bokeh plots                 | Yes             | Yes                 | Yes             | No                 | No                     |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Supports Plotly plots                | Yes             | Yes                 | No              | No                 | Yes                    |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Supports R ggplot plots              | Yes             | No                  | No              | Yes                | No                     |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Separates content from presentation  | Yes             | Could eventually    | No              | No                 | No                     |
|                                     |                 | using traitlets     |                 |                    |                        |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
|Servable from public site            | Possible        | As live notebooks   | Possible        | Yes, shinyapps.io  | Yes, Plotly Cloud      |
|                                     | with mybinder   | via mybinder        | with mybinder   |                    |                        |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+
+Servable in enterprise platform      | Yes, AE5        | Yes, in AE5, using  | Yes, AE5        | Yes, Shiny Server, | Yes, Plotly Enterprise |
|                                     |                 | read-only cells     |                 | +AE5?              |                        |
+-------------------------------------+-----------------+---------------------+-----------------+--------------------+------------------------+


