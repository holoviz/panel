Roadmap
=======

(As of 10/2018)

The Panel library is new, but it builds on at least a decade of work
in previous and related Python projects. Thus there are many parts of Panel
that are very solidly implemented, with features that have been tested
and improved over years of active use by large communities of Bokeh
and Param users. Other features are new to Panel itself or were added
to support Panel, and will gradually become more solid as they get
into widespread use.

The currently funded priority items for development in 2018-2019
include:

1. **Polishing the new features, documentation, and examples**: 
   As issues, bugs, and usabilty gaps are reported on the issue
   tracker, we will address these as time permits.

2. **GridSpec**: Panels can currently be created using ``interact()``
   or as nested ``pn.Row()`` or ``pn.Column()`` objects, potentially with
   ``pn.Spacer()`` objects to adjust spacing.  A complementary approach
   like Matplotlib's
   `GridSpec <https://matplotlib.org/users/gridspec.html>`__ makes it
   simpler to make an arrangement into a regular grid by defining the
   total rows and columns from the start, then assigning individual
   panes to specifc ranges of rows and columns in the grid. An
   `initial implementation <https://github.com/pyviz/panel/pull/31>`__
   is underway, but it will need more work before it becomes usable.
   
3. **Widget improvements**: There are many improvements needed to the
   detais of the provided widgets, such as making numeric values
   editable, improving the stepsize behavior, making layouts more
   compact, lining up widgets better, combining multiple related
   widgets per row, allowing widget groups to be laid out
   horizontally, and so on. These improvements will happen gradually,
   and mostly depend on changes to the underlying Bokeh library.
   
Other features we'd love to see in Panel but which are not currently
funded or scheduled include:
   
1. **Static export**: Panel widgets are currently only "live" when
   backed by a Python server, but in many cases the mapping from widget
   to displayed object follows a well-defined pattern, which can
   be captured in JavaScript code that runs with or without a Python
   process. Supporting static export to .html that can be sent in an
   email or posted on any website will require capturing these
   typical communication patterns, as well as providing a set
   of communication channels to ship with exported documents. Examples
   of the results of this general approach are on
   `holoviews.org <http://holoviews.org>`__, but
   Panel will need its own separate implementation for static export.

2. **Other plotting libraries**: Panel already supports a wide variety
   of libraries, including all the libraries currently in use by the
   authors or their collaborators.  Most other libraries can trivially
   be supported as well, if anyone can provide an example of a plot
   already supported by Panel converted into this other library.
   As mentioned in 
   `issue 2 <https://github.com/pyviz/panel/issues/2>`__, 
   the ipywidgets-based libraries will be more complicated to support,
   but any library that produces PNG, SVG, HTML, or another basic
   type should be very straightforward to include.

3. **Themes**: By default, Panel apps use Bokeh's default theming,
   but other look-and-feel options can be provided by using other
   available Bokeh themes, making your own, or embedding into a Bokeh
   Jinja2 template. We'll add examples of such theming to the Panel
   website as we develop them.

4. **Responsive sizing**: Panel objects (panes and similar viewable
   items) currently accept a fixed height and width in pixels.  In
   many cases, it's desirable to have at least some of the objects
   responsively adjust to the screen size available, so that they can
   make use of whatever screen or window area is available. Responsive
   sizing can be implemented once Bokeh's current layout-refactoring
   project has been completed.
   
5. **BI tools**: Panel is designed for displaying content that you
   already have developed in a Jupyter notebook, but it could also
   be used as a way for building business-intelligence-style
   dashboards that mix traditional Python plotting output with
   BI-style indicators like speedometers, single number displays
   (e.g. stock tickers), and so on.  Adding a small number of
   such plots or widgets could help make it simpler to build
   BI-type dashboards where the content comes directly from
   Python.

6. **Jupyter notebook extension**: The Jupyter-Dashboards project
   provided a `Jupyter extension <https://jupyter-dashboards-layout.readthedocs.io>`__
   allowing drag and drop layout for Jupyter notebook cells. This
   approach worked well in many cases, but the underlying server used
   for deployment is no longer maintained, and so that approach remains
   only a proof of concept. Panel, on the other hand, is fully deployable
   outside of the notebook as well as in it, and so it would be great
   to have a drag-and-drop interface either based on the
   Jupyter-Dashboards project or developed separately to provide similar
   capabilities. As for Jupyter Dashboards, the layout information
   could be stored as cell metadata in the notebook, providing hints
   for Panel to set up the dashboard layout when served separately.
   There are likely to be tricky issues with control flow that would
   need to be addressed when a notebook is used in a non-linear
   dashboard in this way.

7. **Support for Traitlets**: Panel currently supports declarative user 
   interfaces for objects defined using the Param library, and similar
   support could be added for objects defined using the Traitlets
   library. Traitlets and Param offer similar functionality, so the
   benefit of adding Traitlets support would primarily be for users
   who have large bodies of code already written as traitlets.   

If any of the functionality above is interesting to you (or you have
ideas of your own!) and can offer help with implementation, please
open an issue on this repository. And if you are lucky enough to be in
a position to fund our developers to work on it, please contact
``sales@anaconda.com``.
