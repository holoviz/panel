import param

from bokeh.document import Document
from bokeh.io import curdoc, show
from bokeh.layouts import Column as BkColumn, Row as BkRow

from .comms import JupyterCommManager
from .util import Renderer, render, add_to_doc


class Viewable(param.Parameterized):
    """
    A Viewable is an abstract baseclass for objects which wrap bokeh
    models and display them using the PyViz display and comms machinery.
    """

    __abstract = True

    def _get_model(self, doc, comm=None, plot_id=None):
        """
        Should return the bokeh model to be rendered. 
        """

    def _repr_mimebundle_(self, include=None, exclude=None):
        doc = Document()
        comm = JupyterCommManager.get_server_comm()
        return render(self._get_model(doc, comm), doc, comm)

    def server_doc(self, doc=None):
        doc = doc or curdoc()
        model = self._get_model(doc)
        add_to_doc(model, doc)
        return doc

    def _modify_doc(self, doc):
        return self.server_doc(doc)

    def app(self, notebook_url="localhost:8888"):
        """
        Displays a bokeh server app in the notebook.
        """
        show(self._modify_doc, notebook_url=notebook_url)



class View(Viewable):
    """
    A wrapper for bokeh plots and objects that can be converted to
    bokeh plots.
    """

    def __init__(self, obj, **params):
        self.object = obj
        super(View, self).__init__(**params)

    def _get_model(self, doc, comm=None, plot_id=None, container=None):
        """
        Should return the bokeh model to be rendered. 
        """
        is_root = container is None
        if is_root:
            container = BkColumn()
        plot = Renderer.render(self.object, doc, plot_id, comm, container)
        if is_root:
            container.children = [plot]
            return container
        return plot


class Layout(Viewable):
    """
    Abstract baseclass for a Layout of Viewables.
    """

    children = param.List(default=[])

    _bokeh_model = None

    __abstract = True

    def __init__(self, *children, **params):
        super(Layout, self).__init__(children=list(children), **params)
    
    def _get_model(self, doc, comm=None, plot_id=None, container=None):
        """
        Should return the bokeh model to be rendered. 
        """
        model = self._bokeh_model()
        plot_id = model.ref['id'] if plot_id is None else plot_id
        children = []
        for child in self.children:
            if not isinstance(child, Viewable):
                child = View(child)
            children.append(child._get_model(doc, comm, plot_id, model))
        model.children = children
        return model


class Row(Layout):
    """
    Horizontal layout of Viewables.
    """

    _bokeh_model = BkRow


class Column(Layout):
    """
    Vertical layout of Viewables.
    """

    _bokeh_model = BkColumn
