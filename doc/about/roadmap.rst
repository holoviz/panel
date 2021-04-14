Roadmap
=======

(As of 11/2019)

Panel is a stable library at this point in time and the major roadmap
items mainly include adding new components and making it easier to
achieve a polished look and feel for complicated applications. The
main roadmap items icnlude:

1. **Other plotting & widget libraries**: Panel already supports a
   wide variety of libraries, including all the libraries currently in
   use by the authors or their collaborators.  Most other libraries
   can trivially be supported as well, if anyone can provide an
   example of a plot already supported by Panel converted into this
   other library.  As mentioned in `issue 2
   <https://github.com/pyviz/panel/issues/2>`__, we will be working on
   bringing ipywidgets-based components to Panel.

2. **Themes and Templates**: By default, Panel apps use Bokeh's
   default theming, but other look-and-feel options can be provided by
   using other available Bokeh themes, making your own, or embedding
   into a Bokeh Jinja2 template. We'll add examples of such theming
   and provide a range of custom templates to achieve a polished look
   and feel in the coming releases.

3. **BI tools**: Panel is designed for displaying content that you
   already have developed in a Jupyter notebook, but it could also
   be used as a way for building business-intelligence-style
   dashboards that mix traditional Python plotting output with
   BI-style indicators like speedometers, single number displays
   (e.g. stock tickers), and so on.  Adding a small number of
   such plots or widgets could help make it simpler to build
   BI-type dashboards where the content comes directly from
   Python.

4. **Jupyter notebook extension**: The Jupyter-Dashboards project
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

5. **Support for Traitlets**: Panel currently supports declarative user 
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
